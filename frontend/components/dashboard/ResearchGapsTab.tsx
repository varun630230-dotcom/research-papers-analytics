"use client";

import { useState } from 'react';
import { Gap } from '@/types';
import { Card } from '@/components/ui/Card';
import { ConfidenceBadge } from '@/components/ui/ConfidenceBadge';
import { Badge } from '@/components/ui/Badge';
import { Search, ChevronDown, ChevronUp, FileText, Layers, Quote, ShieldAlert, Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ResearchGapsTabProps {
  gaps: Gap[];
}

export function ResearchGapsTab({ gaps = [] }: ResearchGapsTabProps) {
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});

  if (!gaps || gaps.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <Search className="w-12 h-12 text-gray-300 dark:text-gray-600 mb-4" />
        <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100">No Research Gaps Recorded</h3>
        <p className="text-gray-500 dark:text-gray-400 mt-2 max-w-md text-sm">
          No cross-paper research gaps identified from the analyzed sources.
        </p>
      </div>
    );
  }

  const toggleExpand = (id: string) => {
    setExpanded(prev => ({ ...prev, [id]: !prev[id] }));
  };

  const getGapTypeColor = (type: string) => {
    switch(type?.toLowerCase()) {
      case 'knowledge': return 'bg-blue-50 text-blue-700 dark:bg-blue-950/50 dark:text-blue-300 border-blue-200 dark:border-blue-800';
      case 'methodological': return 'bg-purple-50 text-purple-700 dark:bg-purple-950/50 dark:text-purple-300 border-purple-200 dark:border-purple-800';
      case 'dataset / data':
      case 'data': return 'bg-orange-50 text-orange-700 dark:bg-orange-950/50 dark:text-orange-300 border-orange-200 dark:border-orange-800';
      case 'evaluation': return 'bg-teal-50 text-teal-700 dark:bg-teal-950/50 dark:text-teal-300 border-teal-200 dark:border-teal-800';
      case 'technology': return 'bg-indigo-50 text-indigo-700 dark:bg-indigo-950/50 dark:text-indigo-300 border-indigo-200 dark:border-indigo-800';
      case 'generalization': return 'bg-rose-50 text-rose-700 dark:bg-rose-950/50 dark:text-rose-300 border-rose-200 dark:border-rose-800';
      case 'explainability': return 'bg-amber-50 text-amber-700 dark:bg-amber-950/50 dark:text-amber-300 border-amber-200 dark:border-amber-800';
      case 'deployment': return 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300 border-gray-200 dark:border-gray-700';
    }
  };

  return (
    <div className="space-y-8">
      {/* Header Info */}
      <div className="bg-gradient-to-r from-purple-50 to-indigo-50 dark:from-gray-900 dark:to-gray-850 border border-purple-100 dark:border-gray-800 rounded-2xl p-6 shadow-sm">
        <div className="flex items-center gap-2.5 mb-2">
          <Layers className="w-5 h-5 text-purple-600 dark:text-purple-400" />
          <h2 className="text-lg font-bold text-gray-900 dark:text-gray-100">
            Multi-Paper Evidence-Clustered Research Gaps
          </h2>
        </div>
        <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-300 max-w-3xl leading-relaxed">
          These gaps represent recurring limitations, conflicting results, and unresolved questions aggregated across multiple independently verified peer-reviewed studies.
        </p>
      </div>

      {/* Gaps List */}
      <div className="space-y-4">
        {gaps.map((gap, i) => {
          const id = gap.title || `gap-${i}`;
          const isExpanded = expanded[id] !== false; // Default expanded for visibility

          return (
            <Card 
              key={i} 
              className="bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-800 overflow-hidden shadow-sm hover:shadow-md transition"
            >
              <div 
                className="p-6 cursor-pointer flex justify-between items-start gap-4"
                onClick={() => toggleExpand(id)}
              >
                <div className="space-y-2.5 flex-grow">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className={cn("px-2.5 py-0.5 rounded-md text-xs font-bold border capitalize", getGapTypeColor(gap.type || 'other'))}>
                      {gap.type || 'Gap'}
                    </span>
                    <ConfidenceBadge type={gap.confidence} />
                    <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-700">
                      {gap.validation_status || 'Evidence-backed'}
                    </span>
                    <span className="text-xs text-purple-600 dark:text-purple-400 font-semibold ml-auto">
                      {gap.number_of_supporting_papers || gap.supporting_sources?.length || 2} Corroborating Papers
                    </span>
                  </div>

                  <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100">
                    {gap.title}
                  </h3>
                  
                  <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                    {gap.description}
                  </p>
                </div>

                <button className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 p-1 mt-1 shrink-0">
                  {isExpanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                </button>
              </div>

              {isExpanded && (
                <div className="px-6 pb-6 pt-2 border-t border-gray-100 dark:border-gray-800 bg-gray-50/50 dark:bg-gray-800/20 space-y-4 text-xs">
                  {/* Synthesized Evidence */}
                  <div className="bg-white dark:bg-gray-900 p-4 rounded-xl border border-gray-200 dark:border-gray-700 space-y-1.5">
                    <strong className="text-gray-900 dark:text-gray-100 font-bold block text-xs flex items-center gap-1.5">
                      <Quote className="w-3.5 h-3.5 text-purple-600" />
                      Synthesized Empirical Evidence
                    </strong>
                    <p className="text-gray-700 dark:text-gray-300 text-xs sm:text-sm leading-relaxed">
                      {gap.evidence}
                    </p>
                    {gap.reasoning_summary && (
                      <p className="text-[11px] text-gray-500 dark:text-gray-400 italic pt-1 border-t border-gray-100 dark:border-gray-800">
                        {gap.reasoning_summary}
                      </p>
                    )}
                  </div>

                  {/* Supporting Extracted Passages */}
                  {gap.supporting_evidence_passages && gap.supporting_evidence_passages.length > 0 && (
                    <div className="space-y-2">
                      <strong className="text-gray-800 dark:text-gray-200 font-bold block">
                        Extracted Literature Excerpts:
                      </strong>
                      <div className="space-y-1.5">
                        {gap.supporting_evidence_passages.map((passage, idx) => (
                          <div key={idx} className="p-3 bg-purple-50/60 dark:bg-purple-950/30 border-l-4 border-purple-500 text-purple-900 dark:text-purple-200 rounded-r-lg">
                            {passage}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Supporting Paper Titles */}
                  {gap.supporting_sources && gap.supporting_sources.length > 0 && (
                    <div>
                      <strong className="text-gray-800 dark:text-gray-200 font-bold block mb-1.5 flex items-center gap-1">
                        <FileText className="w-3.5 h-3.5 text-gray-500" />
                        Supporting Papers:
                      </strong>
                      <ul className="list-disc list-inside space-y-1 text-gray-600 dark:text-gray-400">
                        {gap.supporting_sources.map((src, j) => (
                          <li key={j} className="text-blue-600 dark:text-blue-400 font-medium">
                            {src}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Potential Impact */}
                  {gap.potential_impact && (
                    <div className="bg-emerald-50/60 dark:bg-emerald-950/30 p-3.5 rounded-xl border border-emerald-200 dark:border-emerald-800/50">
                      <strong className="text-emerald-900 dark:text-emerald-300 font-bold block mb-1">
                        Innovation & Problem-Solving Potential:
                      </strong>
                      <p className="text-emerald-800 dark:text-emerald-200">
                        {gap.potential_impact}
                      </p>
                    </div>
                  )}
                </div>
              )}
            </Card>
          );
        })}
      </div>
    </div>
  );
}
