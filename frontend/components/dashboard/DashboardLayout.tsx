"use client";

import { useState, useRef } from 'react';
import { ProjectResult } from '@/types';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/Button';
import { cn } from '@/lib/utils';
import { Download, ChevronLeft, ChevronRight, Search, Sparkles, CheckCircle2 } from 'lucide-react';

// Import Tabs
import { OverviewTab } from './OverviewTab';
import { ResearchTab } from './ResearchTab';
import { MethodsTab } from './MethodsTab';
import { DatasetsTab } from './DatasetsTab';
import { TechnologyTab } from './TechnologyTab';
import { ExistingSolutionsTab } from './ExistingSolutionsTab';
import { ResearchGapsTab } from './ResearchGapsTab';
import { MarketGapsTab } from './MarketGapsTab';
import { OpportunitiesTab } from './OpportunitiesTab';
import { NoveltyTab } from './NoveltyTab';
import { RecommendationTab } from './RecommendationTab';
import { ArchitectureTab } from './ArchitectureTab';
import { RoadmapTab } from './RoadmapTab';
import { SourcesTab } from './SourcesTab';

interface DashboardLayoutProps {
  project: ProjectResult;
}

const TABS = [
  'OVERVIEW',
  'RESEARCH',
  'METHODS',
  'DATASETS',
  'TECHNOLOGY',
  'EXISTING SOLUTIONS',
  'RESEARCH GAPS',
  'MARKET GAPS',
  'OPPORTUNITIES',
  'NOVELTY',
  'RECOMMENDED PROJECT',
  'ARCHITECTURE',
  'ROADMAP',
  'SOURCES'
] as const;

type TabType = typeof TABS[number];

export function DashboardLayout({ project }: DashboardLayoutProps) {
  const [activeTab, setActiveTab] = useState<TabType>('OVERVIEW');
  const [isExporting, setIsExporting] = useState(false);
  const tabListRef = useRef<HTMLDivElement>(null);

  const hasData = (project.papers && project.papers.length > 0) || (project.top_papers && project.top_papers.length > 0);

  const handleScroll = (direction: 'left' | 'right') => {
    if (tabListRef.current) {
      const scrollAmount = direction === 'left' ? -220 : 220;
      tabListRef.current.scrollBy({ left: scrollAmount, behavior: 'smooth' });
    }
  };

  const handleExport = async (format: 'markdown' | 'json') => {
    if (!project.id) return;
    try {
      setIsExporting(true);
      const content = await api.exportProject(project.id, format);
      
      const blob = new Blob([content], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url; 
      a.download = `innovate-ai-dossier-${project.id}.${format === 'markdown' ? 'md' : 'json'}`; 
      a.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Export failed', error);
    } finally {
      setIsExporting(false);
    }
  };

  if (!hasData) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-center px-4">
        <div className="w-16 h-16 bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-full flex items-center justify-center mb-6">
          <Search className="w-8 h-8" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">Analysis in Progress</h2>
        <p className="text-gray-500 dark:text-gray-400 max-w-md">
          Start an analysis to generate research intelligence. The dashboard will populate with evidence-backed findings once complete.
        </p>
      </div>
    );
  }

  const renderActiveTab = () => {
    switch (activeTab) {
      case 'OVERVIEW':
        return <OverviewTab project={project} />;
      case 'RESEARCH':
        return <ResearchTab 
          papers={project.papers || []} 
          top_papers={project.top_papers}
          additional_papers={project.additional_papers}
          background_papers={project.background_papers}
          coverage={project.coverage}
          extractions={project.paper_extractions} 
        />;
      case 'METHODS':
        return <MethodsTab methods={project.methods || []} papers={project.top_papers || project.papers || []} />;
      case 'DATASETS':
        return <DatasetsTab datasets={project.datasets || []} />;
      case 'TECHNOLOGY':
        return <TechnologyTab technologies={project.technologies} />;
      case 'EXISTING SOLUTIONS':
        return <ExistingSolutionsTab solutions={project.existing_solutions || []} />;
      case 'RESEARCH GAPS':
        return <ResearchGapsTab gaps={project.research_gaps || []} />;
      case 'MARKET GAPS':
        return <MarketGapsTab gaps={project.market_gaps || []} />;
      case 'OPPORTUNITIES':
        return <OpportunitiesTab opportunities={project.opportunities || []} />;
      case 'NOVELTY':
        return <NoveltyTab novelty={project.novelty} />;
      case 'RECOMMENDED PROJECT':
        return <RecommendationTab recommendation={project.recommendation} />;
      case 'ARCHITECTURE':
        return <ArchitectureTab architecture={project.architecture} />;
      case 'ROADMAP':
        return <RoadmapTab roadmap={project.roadmap || []} />;
      case 'SOURCES':
        return <SourcesTab sources={project.sources || []} />;
      default:
        return <OverviewTab project={project} />;
    }
  };

  return (
    <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header Banner */}
      <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
        <div className="space-y-1.5 max-w-3xl">
          <div className="flex items-center gap-2.5">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800">
              <CheckCircle2 className="w-3.5 h-3.5" />
              Verified Evidence Dossier
            </span>
            <span className="text-xs text-gray-500 dark:text-gray-400 font-mono">
              ID: {project.id?.substring(0, 8)}...
            </span>
          </div>
          <h1 className="text-xl sm:text-2xl font-extrabold text-gray-900 dark:text-gray-100 leading-tight">
            {project.idea}
          </h1>
          <div className="flex flex-wrap items-center gap-4 text-xs sm:text-sm text-gray-500 dark:text-gray-400">
            <span><strong className="text-gray-700 dark:text-gray-300">Domain:</strong> {project.domain || project.idea_analysis?.problem_domain || 'AI Research'}</span>
            <span>•</span>
            <span><strong className="text-gray-700 dark:text-gray-300">Goal:</strong> {project.goal || 'Research Project'}</span>
            <span>•</span>
            <span><strong className="text-gray-700 dark:text-gray-300">Level:</strong> {project.technical_level || 'Intermediate'}</span>
          </div>
        </div>

        {/* Export Buttons */}
        <div className="flex items-center gap-2.5 self-end md:self-center shrink-0">
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleExport('markdown')}
            disabled={isExporting}
            className="flex items-center gap-2"
          >
            <Download className="w-4 h-4" />
            Export Markdown
          </Button>
          <Button
            variant="primary"
            size="sm"
            onClick={() => handleExport('json')}
            disabled={isExporting}
            className="flex items-center gap-2"
          >
            <Download className="w-4 h-4" />
            Export JSON
          </Button>
        </div>
      </div>

      {/* Sleek Horizontal Tab Bar */}
      <div className="relative bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl shadow-sm p-1.5">
        <div className="flex items-center">
          <button
            onClick={() => handleScroll('left')}
            className="hidden sm:flex items-center justify-center p-1.5 rounded-lg text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 transition z-10 shrink-0 mr-1"
            title="Scroll tabs left"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>

          <div
            ref={tabListRef}
            className="flex space-x-1.5 overflow-x-auto scrollbar-none py-1 scroll-smooth w-full no-scrollbar"
            style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
          >
            {TABS.map((tab) => {
              const isActive = activeTab === tab;
              return (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={cn(
                    "px-3.5 py-2 text-xs sm:text-sm font-semibold rounded-lg whitespace-nowrap transition-all duration-150 shrink-0",
                    isActive
                      ? "bg-blue-600 text-white shadow-sm"
                      : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 hover:bg-gray-100 dark:hover:bg-gray-800"
                  )}
                >
                  {tab}
                </button>
              );
            })}
          </div>

          <button
            onClick={() => handleScroll('right')}
            className="hidden sm:flex items-center justify-center p-1.5 rounded-lg text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 transition z-10 shrink-0 ml-1"
            title="Scroll tabs right"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Main Tab Content */}
      <div className="min-h-[500px]">
        {renderActiveTab()}
      </div>
    </div>
  );
}
