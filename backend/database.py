"""
ResearchGap AI - Database Module
=================================
Manages the SQLite database: creates tables, provides functions
for inserting and retrieving data.

Why SQLite?
- Zero setup (no database server to install)
- Single file (easy to backup, move, delete)
- Built into Python (no extra drivers needed)
- Perfect for a single-user research tool

Why raw SQL instead of an ORM like SQLAlchemy?
- Teaches you actual SQL
- Fewer abstractions to understand
- Easier to debug
- Good enough for this application's needs
"""

import sqlite3
import json
import os
from datetime import datetime
from config import config


def get_database_path():
    """Returns the absolute path to the database file."""
    return os.path.abspath(config["DATABASE_PATH"])


def get_connection():
    """
    Creates and returns a database connection.
    
    row_factory = sqlite3.Row makes query results accessible
    by column name (like a dictionary) instead of just index.
    Example: row["title"] instead of row[0]
    """
    db_path = get_database_path()
    
    # Create the data directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row  # Access columns by name
    connection.execute("PRAGMA journal_mode=WAL")  # Better concurrent access
    connection.execute("PRAGMA foreign_keys=ON")  # Enforce relationships
    return connection


def initialize_database():
    """
    Creates all database tables if they don't exist.
    
    Called once when the application starts.
    Using IF NOT EXISTS means it's safe to call multiple times.
    """
    connection = get_connection()
    cursor = connection.cursor()
    
    # -------------------------------------------------------------------------
    # Table: research_projects
    # Stores each research analysis session
    # -------------------------------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS research_projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            description TEXT DEFAULT '',
            domain TEXT DEFAULT '',
            keywords TEXT DEFAULT '',
            objectives TEXT DEFAULT '',
            status TEXT DEFAULT 'pending',
            total_papers_found INTEGER DEFAULT 0,
            relevant_papers INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)
    
    # -------------------------------------------------------------------------
    # Table: papers
    # Stores discovered research papers
    # Each paper belongs to a research project (foreign key)
    # -------------------------------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS papers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            authors TEXT DEFAULT '',
            abstract TEXT DEFAULT '',
            publication_date TEXT DEFAULT '',
            doi TEXT DEFAULT '',
            url TEXT DEFAULT '',
            pdf_url TEXT DEFAULT '',
            source TEXT DEFAULT '',
            relevance_score REAL DEFAULT 0.0,
            is_relevant INTEGER DEFAULT 1,
            pdf_text TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (project_id) REFERENCES research_projects(id)
        )
    """)
    
    # -------------------------------------------------------------------------
    # Table: paper_analyses
    # Stores Gemini's analysis of individual papers
    # -------------------------------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS paper_analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paper_id INTEGER NOT NULL,
            project_id INTEGER NOT NULL,
            analysis_data TEXT DEFAULT '{}',
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (paper_id) REFERENCES papers(id),
            FOREIGN KEY (project_id) REFERENCES research_projects(id)
        )
    """)
    
    # -------------------------------------------------------------------------
    # Table: research_results
    # Stores the aggregated analysis results for a project
    # (synthesis, gaps, opportunities, scores, etc.)
    # -------------------------------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS research_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL UNIQUE,
            synthesis TEXT DEFAULT '{}',
            research_gaps TEXT DEFAULT '[]',
            tech_limitations TEXT DEFAULT '[]',
            market_opportunities TEXT DEFAULT '[]',
            opportunity_scores TEXT DEFAULT '[]',
            novelty_assessment TEXT DEFAULT '{}',
            architecture TEXT DEFAULT '{}',
            roadmap TEXT DEFAULT '{}',
            ai_review TEXT DEFAULT '{}',
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (project_id) REFERENCES research_projects(id)
        )
    """)
    
    connection.commit()
    connection.close()
    print(f"Database initialized at: {get_database_path()}")


# =============================================================================
# RESEARCH PROJECT OPERATIONS
# =============================================================================

def create_project(topic, description="", domain="", keywords="", objectives=""):
    """
    Creates a new research project and returns its ID.
    
    Parameters:
        topic: The main research topic (required)
        description: Detailed description of the research idea
        domain: Research domain (e.g., "Machine Learning", "Healthcare")
        keywords: Comma-separated keywords for paper search
        objectives: What the researcher wants to achieve
    
    Returns:
        The ID of the newly created project
    """
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute(
        """
        INSERT INTO research_projects (topic, description, domain, keywords, objectives)
        VALUES (?, ?, ?, ?, ?)
        """,
        (topic, description, domain, keywords, objectives)
    )
    
    project_id = cursor.lastrowid
    connection.commit()
    connection.close()
    return project_id


def get_project(project_id):
    """
    Retrieves a single research project by its ID.
    Returns a dictionary or None if not found.
    """
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute("SELECT * FROM research_projects WHERE id = ?", (project_id,))
    row = cursor.fetchone()
    connection.close()
    
    if row is None:
        return None
    return dict(row)


def get_all_projects():
    """
    Retrieves all research projects, ordered by most recent first.
    Returns a list of dictionaries.
    """
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute("SELECT * FROM research_projects ORDER BY created_at DESC")
    rows = cursor.fetchall()
    connection.close()
    
    return [dict(row) for row in rows]


def update_project_status(project_id, status, total_papers=None, relevant_papers=None):
    """
    Updates the status and paper counts for a project.
    
    Status values: 'pending', 'searching', 'analyzing', 'completed', 'failed'
    """
    connection = get_connection()
    cursor = connection.cursor()
    
    updates = ["status = ?", "updated_at = datetime('now')"]
    values = [status]
    
    if total_papers is not None:
        updates.append("total_papers_found = ?")
        values.append(total_papers)
    
    if relevant_papers is not None:
        updates.append("relevant_papers = ?")
        values.append(relevant_papers)
    
    values.append(project_id)
    
    cursor.execute(
        f"UPDATE research_projects SET {', '.join(updates)} WHERE id = ?",
        values
    )
    
    connection.commit()
    connection.close()


# =============================================================================
# PAPER OPERATIONS
# =============================================================================

def save_papers(project_id, papers):
    """
    Saves a list of paper dictionaries to the database.
    
    Parameters:
        project_id: The research project these papers belong to
        papers: List of paper dictionaries with normalized fields
    
    Returns:
        Number of papers saved
    """
    connection = get_connection()
    cursor = connection.cursor()
    
    count = 0
    for paper in papers:
        cursor.execute(
            """
            INSERT INTO papers 
                (project_id, title, authors, abstract, publication_date,
                 doi, url, pdf_url, source, relevance_score, is_relevant)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                project_id,
                paper.get("title", ""),
                paper.get("authors", ""),
                paper.get("abstract", ""),
                paper.get("publication_date", ""),
                paper.get("doi", ""),
                paper.get("url", ""),
                paper.get("pdf_url", ""),
                paper.get("source", ""),
                paper.get("relevance_score", 0.0),
                1 if paper.get("is_relevant", True) else 0,
            )
        )
        count += 1
    
    connection.commit()
    connection.close()
    return count


def get_papers(project_id, relevant_only=False):
    """
    Retrieves all papers for a research project.
    
    Parameters:
        project_id: The research project ID
        relevant_only: If True, only return papers marked as relevant
    
    Returns:
        List of paper dictionaries
    """
    connection = get_connection()
    cursor = connection.cursor()
    
    query = "SELECT * FROM papers WHERE project_id = ?"
    params = [project_id]
    
    if relevant_only:
        query += " AND is_relevant = 1"
    
    query += " ORDER BY relevance_score DESC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    connection.close()
    
    return [dict(row) for row in rows]


def update_paper_pdf_text(paper_id, pdf_text):
    """Stores extracted PDF text for a paper."""
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute(
        "UPDATE papers SET pdf_text = ? WHERE id = ?",
        (pdf_text, paper_id)
    )
    
    connection.commit()
    connection.close()


# =============================================================================
# ANALYSIS OPERATIONS
# =============================================================================

def save_paper_analysis(paper_id, project_id, analysis_data):
    """
    Saves the AI analysis of a single paper.
    analysis_data is a dictionary that gets stored as JSON.
    """
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute(
        """
        INSERT INTO paper_analyses (paper_id, project_id, analysis_data)
        VALUES (?, ?, ?)
        """,
        (paper_id, project_id, json.dumps(analysis_data))
    )
    
    connection.commit()
    connection.close()


def get_paper_analyses(project_id):
    """
    Retrieves all paper analyses for a project.
    Parses the JSON analysis_data back into dictionaries.
    """
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute(
        "SELECT * FROM paper_analyses WHERE project_id = ?",
        (project_id,)
    )
    rows = cursor.fetchall()
    connection.close()
    
    results = []
    for row in rows:
        item = dict(row)
        # Parse the JSON string back into a dictionary
        try:
            item["analysis_data"] = json.loads(item["analysis_data"])
        except json.JSONDecodeError:
            item["analysis_data"] = {}
        results.append(item)
    
    return results


def save_research_results(project_id, results):
    """
    Saves or updates the aggregated research results for a project.
    
    Parameters:
        project_id: The research project ID
        results: Dictionary containing synthesis, gaps, opportunities, etc.
    """
    connection = get_connection()
    cursor = connection.cursor()
    
    # Use INSERT OR REPLACE since project_id is UNIQUE
    cursor.execute(
        """
        INSERT OR REPLACE INTO research_results 
            (project_id, synthesis, research_gaps, tech_limitations,
             market_opportunities, opportunity_scores, novelty_assessment,
             architecture, roadmap, ai_review, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """,
        (
            project_id,
            json.dumps(results.get("synthesis", {})),
            json.dumps(results.get("research_gaps", [])),
            json.dumps(results.get("tech_limitations", [])),
            json.dumps(results.get("market_opportunities", [])),
            json.dumps(results.get("opportunity_scores", [])),
            json.dumps(results.get("novelty_assessment", {})),
            json.dumps(results.get("architecture", {})),
            json.dumps(results.get("roadmap", {})),
            json.dumps(results.get("ai_review", {})),
        )
    )
    
    connection.commit()
    connection.close()


def get_research_results(project_id):
    """
    Retrieves the aggregated research results for a project.
    Parses all JSON fields back into Python objects.
    """
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute(
        "SELECT * FROM research_results WHERE project_id = ?",
        (project_id,)
    )
    row = cursor.fetchone()
    connection.close()
    
    if row is None:
        return None
    
    result = dict(row)
    
    # Parse all JSON fields
    json_fields = [
        "synthesis", "research_gaps", "tech_limitations",
        "market_opportunities", "opportunity_scores",
        "novelty_assessment", "architecture", "roadmap", "ai_review"
    ]
    
    for field in json_fields:
        try:
            result[field] = json.loads(result[field])
        except (json.JSONDecodeError, TypeError):
            result[field] = {} if field in ["synthesis", "novelty_assessment", "architecture", "roadmap", "ai_review"] else []
    
    return result


def delete_project(project_id):
    """
    Deletes a project and all associated data.
    Foreign key cascading is not enabled by default in SQLite,
    so we delete related records manually.
    """
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute("DELETE FROM research_results WHERE project_id = ?", (project_id,))
    cursor.execute("DELETE FROM paper_analyses WHERE project_id = ?", (project_id,))
    cursor.execute("DELETE FROM papers WHERE project_id = ?", (project_id,))
    cursor.execute("DELETE FROM research_projects WHERE id = ?", (project_id,))
    
    connection.commit()
    connection.close()
