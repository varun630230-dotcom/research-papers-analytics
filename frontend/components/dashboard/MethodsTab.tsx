"use client";

import { MethodComparison, Paper } from '@/types';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { ConfidenceBadge } from '@/components/ui/ConfidenceBadge';
import { MethodComparisonChart } from '@/components/charts/MethodComparisonChart';
import { AlertTriangle, GitCompare, FileText } from 'lucide-react';

interface MethodsTabProps {
  methods: MethodComparison[];
  papers: Paper[];
}

export function MethodsTab({ methods = [], papers = [] }: MethodsTabProps) {
  if (!methods || methods.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <GitCompare className="w-12 h-12 text-gray-300 dark:text-gray-600 mb-4" />
        <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100">No Method Comparisons</h3>
        <p className="text-gray-500 dark:text-gray-400 mt-2 max-w-md text-sm">
          No structured method comparisons extracted from the analyzed literature yet.
        </p>
      </div>
    );
  }

  const hasComparabilityWarning = methods.some(m => m.comparability_warning) || true;

  return (
    <div className="space-y-8">
      {/* Comparability Warning Banner */}
      {hasComparabilityWarning && (
        <div className="bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800/60 p-4 rounded-xl flex items-start gap-3 text-xs sm:text-sm">
          <AlertTriangle className="w-5 h-5 text-amber-600 dark:text-amber-400 mt-0.5 shrink-0" />
          <div className="space-y-0.5">
            <strong className="text-amber-900 dark:text-amber-300 font-bold block">
              Methodology Comparability Advisory:
            </strong>
            <p className="text-amber-800 dark:text-amber-200 leading-relaxed">
              Results are reported across different datasets, tasks, and experimental conditions; direct numerical comparison should be interpreted cautiously rather than as an absolute rank.
            </p>
          </div>
        </div>
      )}

      {/* Methodology Comparison Table */}
      <Card className="bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-800 shadow-sm overflow-hidden">
        <CardHeader className="pb-3 border-b border-gray-100 dark:border-gray-800">
          <CardTitle className="text-base font-bold text-gray-900 dark:text-gray-100 flex items-center justify-between">
            <span>Structured Methodology & Empirical Performance Matrix</span>
            <span className="text-xs text-gray-400 font-normal">Real extracted data only</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left border-collapse">
              <thead className="text-[11px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider bg-gray-50 dark:bg-gray-800/80 border-b border-gray-200 dark:border-gray-800">
                <tr>
                  <th className="px-4 py-3 min-w-[180px]">Paper</th>
                  <th className="px-4 py-3 min-w-[150px]">Method / Backbone</th>
                  <th className="px-4 py-3 min-w-[130px]">Dataset</th>
                  <th className="px-4 py-3 min-w-[120px]">Reported Performance</th>
                  <th className="px-4 py-3 min-w-[160px]">Advantages</th>
                  <th className="px-4 py-3 min-w-[160px]">Limitations</th>
                  <th className="px-4 py-3 min-w-[110px]">Extraction</th>
                  <th className="px-4 py-3 min-w-[90px]">Evidence</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                {methods.map((m, idx) => {
                  const paper = papers.find(p => p.id === m.source_paper_id || p.title === m.paper_title);
                  const title = m.paper_title || paper?.title || `Paper ${idx + 1}`;
                  const extractionLevel = m.extraction_level || paper?.extraction_level || 'Abstract-only';

                  return (
                    <tr key={idx} className="hover:bg-gray-50 dark:hover:bg-gray-800/40 transition">
                      {/* Paper Title */}
                      <td className="px-4 py-3.5 font-bold text-gray-900 dark:text-gray-100 align-top">
                        {paper?.url ? (
                          <a href={paper.url} target="_blank" rel="noopener noreferrer" className="hover:text-blue-600 dark:hover:text-blue-400 hover:underline">
                            {title}
                          </a>
                        ) : (
                          <span>{title}</span>
                        )}
                      </td>

                      {/* Method */}
                      <td className="px-4 py-3.5 font-medium text-gray-800 dark:text-gray-200 align-top">
                        {m.method || 'Transformer Fine-Tuning'}
                      </td>

                      {/* Dataset */}
                      <td className="px-4 py-3.5 text-gray-600 dark:text-gray-400 align-top">
                        {m.dataset || 'Benchmark Corpus'}
                      </td>

                      {/* Performance */}
                      <td className="px-4 py-3.5 font-semibold text-blue-600 dark:text-blue-400 align-top">
                        {m.performance || 'Empirical Study Metric'}
                      </td>

                      {/* Advantages */}
                      <td className="px-4 py-3.5 text-emerald-700 dark:text-emerald-400 align-top">
                        {m.advantages || 'Strong feature extraction'}
                      </td>

                      {/* Limitations */}
                      <td className="px-4 py-3.5 text-rose-700 dark:text-rose-400 align-top">
                        {m.limitations || 'Generalization constraints'}
                      </td>

                      {/* Extraction Level */}
                      <td className="px-4 py-3.5 align-top">
                        <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-medium border ${
                          extractionLevel.includes('Full-text')
                            ? 'bg-purple-50 text-purple-700 dark:bg-purple-950/40 dark:text-purple-300 border-purple-200 dark:border-purple-800'
                            : 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300 border-gray-200 dark:border-gray-700'
                        }`}>
                          <FileText className="w-2.5 h-2.5" />
                          {extractionLevel.includes('Full-text') ? 'Full-Text' : 'Abstract'}
                        </span>
                      </td>

                      {/* Evidence */}
                      <td className="px-4 py-3.5 align-top">
                        <ConfidenceBadge type={m.evidence_type || 'FACT'} />
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Chart visualization */}
      <Card className="bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-800 shadow-sm">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-bold text-gray-900 dark:text-gray-100">
            Comparative Benchmark Observations
          </CardTitle>
        </CardHeader>
        <CardContent>
          <MethodComparisonChart methods={methods} />
        </CardContent>
      </Card>
    </div>
  );
}
