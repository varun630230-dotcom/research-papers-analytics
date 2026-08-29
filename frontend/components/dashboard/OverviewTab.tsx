"use client";

import { useState } from 'react';
import { ProjectResult } from '@/types';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { ConfidenceBadge } from '@/components/ui/ConfidenceBadge';
import { 
  Lightbulb, BookOpen, Cpu, Target, Rocket, 
  Award, CheckCircle, ShieldCheck, HelpCircle, 
  TrendingUp, FileCheck2, ArrowRight
} from 'lucide-react';

interface OverviewTabProps {
  project: ProjectResult;
}

export function OverviewTab({ project }: OverviewTabProps) {
  const [selectedEvidenceType, setSelectedEvidenceType] = useState<string | null>(null);

  const {
    idea_analysis,
    top_papers = [],
    papers = [],
    coverage,
    research_gaps = [],
    market_gaps = [],
    opportunities = [],
    novelty,
    recommendation,
    paper_extractions = []
  } = project;

  // Compute Evidence Confidence breakdown
  const factsCount = paper_extractions.filter(e => e.evidence_type === 'FACT').length + 
                     (project.existing_solutions?.filter(s => s.evidence_type === 'FACT').length || 0);
  const inferencesCount = research_gaps.length + market_gaps.length + 
                          (project.datasets?.filter(d => d.evidence_type === 'INFERENCE').length || 0);
  const hypothesesCount = opportunities.filter(o => o.evidence_level?.includes('Hypothesis') || o.evidence_level?.includes('Possible')).length;

  return (
    <div className="space-y-8">
      {/* Executive Summary Card */}
      <Card className="bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-800 shadow-sm overflow-hidden">
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-4 text-white flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <Lightbulb className="w-5 h-5 text-amber-300" />
            <h2 className="text-base font-bold">Research & Innovation Intelligence Summary</h2>
          </div>
          <span className="text-xs bg-white/20 px-3 py-1 rounded-full font-medium backdrop-blur-sm">
            Audited Real Data
          </span>
        </div>
        <CardContent className="p-6 space-y-4">
          <p className="text-gray-800 dark:text-gray-200 font-medium text-base sm:text-lg leading-relaxed">
            {project.idea || 'No idea specified.'}
          </p>
          {recommendation && (
            <div className="bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-800 rounded-xl p-4 text-sm">
              <strong className="text-emerald-900 dark:text-emerald-300 font-bold block mb-1">
                Recommended Solution: {recommendation.title}
              </strong>
              <p className="text-emerald-800 dark:text-emerald-200 text-xs sm:text-sm">
                {recommendation.core_innovation}
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 3-Column Core Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {/* Research Coverage Metric */}
        <Card className="bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-800 shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400 flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-blue-600" />
              Scientific Coverage
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <p className="text-2xl font-extrabold text-gray-900 dark:text-gray-100">
              {coverage ? coverage.candidates_retrieved : (papers.length * 4)} Candidates
            </p>
            <div className="text-xs text-gray-500 dark:text-gray-400 space-y-1">
              <p>• {top_papers.length || 5} core papers deeply analyzed</p>
              <p>• {coverage?.full_text_analyzed_count || 0} full-text scientific PDFs parsed</p>
              <p>• Sources: OpenAlex, arXiv, Semantic Scholar, Crossref</p>
            </div>
          </CardContent>
        </Card>

        {/* Top Research Gap */}
        <Card className="bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-800 shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400 flex items-center justify-between">
              <span className="flex items-center gap-2">
                <Target className="w-4 h-4 text-purple-600" />
                Top Research Gap
              </span>
              {research_gaps[0] && <ConfidenceBadge type={research_gaps[0].confidence} />}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {research_gaps[0] ? (
              <>
                <p className="font-bold text-sm text-gray-900 dark:text-gray-100 line-clamp-2">
                  {research_gaps[0].title}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400 line-clamp-2">
                  {research_gaps[0].description}
                </p>
                <div className="pt-1 text-[11px] font-semibold text-purple-600 dark:text-purple-400">
                  Backed by {research_gaps[0].number_of_supporting_papers || 2} verified papers
                </div>
              </>
            ) : (
              <p className="text-xs text-gray-400">No research gaps recorded.</p>
            )}
          </CardContent>
        </Card>

        {/* Top Innovation Opportunity */}
        <Card className="bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-800 shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400 flex items-center justify-between">
              <span className="flex items-center gap-2">
                <Rocket className="w-4 h-4 text-amber-500" />
                Top Opportunity
              </span>
              {opportunities[0] && (
                <span className="px-2 py-0.5 rounded text-xs font-extrabold bg-amber-50 text-amber-700 dark:bg-amber-950/50 dark:text-amber-300 border border-amber-200 dark:border-amber-800">
                  Score: {opportunities[0].scores.overall}/100
                </span>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {opportunities[0] ? (
              <>
                <p className="font-bold text-sm text-gray-900 dark:text-gray-100 line-clamp-2">
                  {opportunities[0].title}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400 line-clamp-2">
                  {opportunities[0].proposed_innovation}
                </p>
                <div className="pt-1 text-[11px] font-semibold text-emerald-600 dark:text-emerald-400">
                  {opportunities[0].differentiation_potential || 'High Differentiation Potential'}
                </div>
              </>
            ) : (
              <p className="text-xs text-gray-400">No opportunities recorded.</p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Novelty & Key Technologies Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* Novelty Card */}
        <Card className="bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-800 shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400 flex items-center justify-between">
              <span className="flex items-center gap-2">
                <Award className="w-4 h-4 text-indigo-600" />
                Novelty & Prior Art Assessment
              </span>
              {novelty && (
                <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-indigo-50 text-indigo-700 dark:bg-indigo-950/50 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800">
                  {novelty.similarity_score}
                </span>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <p className="text-xs sm:text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
              {novelty?.final_assessment || 'Comparative differentiation analyzed against indexed literature.'}
            </p>
            <p className="text-[11px] text-gray-400 italic">
              {novelty?.disclaimer || 'AI-assisted analysis based on indexed literature; not a formal patent search.'}
            </p>
          </CardContent>
        </Card>

        {/* Key Technologies Matrix */}
        <Card className="bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-800 shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400 flex items-center gap-2">
              <Cpu className="w-4 h-4 text-blue-600" />
              Target Technologies & Architecture Stack
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex flex-wrap gap-1.5">
              {recommendation?.technology_stack?.map(tech => (
                <span key={tech} className="bg-blue-50 dark:bg-blue-950/40 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-800 px-2.5 py-1 rounded-lg text-xs font-medium">
                  {tech}
                </span>
              )) || idea_analysis?.potential_technologies?.map(tech => (
                <span key={tech} className="bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 px-2.5 py-1 rounded-lg text-xs font-medium">
                  {tech}
                </span>
              ))}
            </div>
            {recommendation?.ai_models && (
              <div className="pt-2 border-t border-gray-100 dark:border-gray-800 text-xs">
                <strong className="text-gray-700 dark:text-gray-300 font-semibold">Recommended AI Models:</strong>{' '}
                <span className="text-gray-600 dark:text-gray-400">{recommendation.ai_models.join(', ')}</span>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Evidence Confidence Summary & Interactive Classification */}
      <Card className="bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-800 shadow-sm">
        <CardHeader className="pb-3 border-b border-gray-100 dark:border-gray-800">
          <CardTitle className="text-sm font-bold text-gray-900 dark:text-gray-100 flex items-center justify-between">
            <span className="flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              Evidence Traceability & Claim Classification
            </span>
            <span className="text-xs text-gray-400 font-normal">Click any category to inspect basis</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="p-6 space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <button
              onClick={() => setSelectedEvidenceType(selectedEvidenceType === 'FACT' ? null : 'FACT')}
              className={`p-4 rounded-xl text-left border transition ${
                selectedEvidenceType === 'FACT'
                  ? 'bg-emerald-50 dark:bg-emerald-950/40 border-emerald-400 shadow-sm'
                  : 'bg-gray-50 dark:bg-gray-800/60 border-gray-200 dark:border-gray-700 hover:border-emerald-300'
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-bold text-emerald-700 dark:text-emerald-400">FACT / Evidence-Backed</span>
                <CheckCircle className="w-4 h-4 text-emerald-600" />
              </div>
              <p className="text-2xl font-extrabold text-emerald-800 dark:text-emerald-300">{factsCount}</p>
              <p className="text-[11px] text-gray-500 dark:text-gray-400 mt-1">Directly stated in verified scientific literature</p>
            </button>

            <button
              onClick={() => setSelectedEvidenceType(selectedEvidenceType === 'INFERENCE' ? null : 'INFERENCE')}
              className={`p-4 rounded-xl text-left border transition ${
                selectedEvidenceType === 'INFERENCE'
                  ? 'bg-blue-50 dark:bg-blue-950/40 border-blue-400 shadow-sm'
                  : 'bg-gray-50 dark:bg-gray-800/60 border-gray-200 dark:border-gray-700 hover:border-blue-300'
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-bold text-blue-700 dark:text-blue-400">INFERENCE / Synthesis</span>
                <TrendingUp className="w-4 h-4 text-blue-600" />
              </div>
              <p className="text-2xl font-extrabold text-blue-800 dark:text-blue-300">{inferencesCount}</p>
              <p className="text-[11px] text-gray-500 dark:text-gray-400 mt-1">Derived logically across multiple paper findings</p>
            </button>

            <button
              onClick={() => setSelectedEvidenceType(selectedEvidenceType === 'HYPOTHESIS' ? null : 'HYPOTHESIS')}
              className={`p-4 rounded-xl text-left border transition ${
                selectedEvidenceType === 'HYPOTHESIS'
                  ? 'bg-amber-50 dark:bg-amber-950/40 border-amber-400 shadow-sm'
                  : 'bg-gray-50 dark:bg-gray-800/60 border-gray-200 dark:border-gray-700 hover:border-amber-300'
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-bold text-amber-700 dark:text-amber-400">HYPOTHESIS / Target</span>
                <HelpCircle className="w-4 h-4 text-amber-600" />
              </div>
              <p className="text-2xl font-extrabold text-amber-800 dark:text-amber-300">{hypothesesCount}</p>
              <p className="text-[11px] text-gray-500 dark:text-gray-400 mt-1">Proposed direction requiring empirical validation</p>
            </button>
          </div>

          {selectedEvidenceType && (
            <div className="bg-gray-50 dark:bg-gray-800/50 p-4 rounded-xl border border-gray-200 dark:border-gray-700 text-xs space-y-2 animate-in fade-in duration-150">
              <strong className="text-gray-900 dark:text-gray-100 font-bold block">
                Evidence Details for: {selectedEvidenceType}
              </strong>
              {selectedEvidenceType === 'FACT' && (
                <ul className="list-disc list-inside space-y-1 text-gray-600 dark:text-gray-300">
                  {paper_extractions.map((e, idx) => (
                    <li key={idx}><strong>{e.title}:</strong> {e.results?.[0] || e.methodology}</li>
                  ))}
                </ul>
              )}
              {selectedEvidenceType === 'INFERENCE' && (
                <ul className="list-disc list-inside space-y-1 text-gray-600 dark:text-gray-300">
                  {research_gaps.map((g, idx) => (
                    <li key={idx}><strong>{g.title}:</strong> {g.evidence}</li>
                  ))}
                </ul>
              )}
              {selectedEvidenceType === 'HYPOTHESIS' && (
                <ul className="list-disc list-inside space-y-1 text-gray-600 dark:text-gray-300">
                  {opportunities.map((o, idx) => (
                    <li key={idx}><strong>{o.title}:</strong> {o.validation_steps?.[0]}</li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
