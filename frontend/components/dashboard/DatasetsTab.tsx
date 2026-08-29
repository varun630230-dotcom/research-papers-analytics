"use client";

import { DatasetInfo } from '@/types';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { ConfidenceBadge } from '@/components/ui/ConfidenceBadge';
import { Badge } from '@/components/ui/Badge';
import { Database, PlusCircle, MinusCircle, AlertCircle, CheckCircle2 } from 'lucide-react';

interface DatasetsTabProps {
  datasets: DatasetInfo[];
}

export function DatasetsTab({ datasets }: DatasetsTabProps) {
  if (!datasets || datasets.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <Database className="w-12 h-12 text-gray-300 dark:text-gray-600 mb-4" />
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">No dataset information</h3>
        <p className="text-gray-500 dark:text-gray-400 mt-2 max-w-md">
          No dataset information was extracted from the analyzed sources.
        </p>
      </div>
    );
  }

  const allGaps = datasets
    .map(d => d.potential_gaps)
    .filter((g): g is string => !!g);

  return (
    <div className="space-y-8">
      {allGaps.length > 0 && (
        <Card className="border-amber-200 bg-amber-50/50 dark:bg-amber-900/10 dark:border-amber-800">
          <CardHeader className="pb-3">
            <CardTitle className="text-lg flex items-center gap-2 text-amber-800 dark:text-amber-400">
              <AlertCircle className="w-5 h-5" />
              Dataset Gaps Identified
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {allGaps.map((gap, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-gray-700 dark:text-gray-300">
                  <div className="w-1.5 h-1.5 rounded-full bg-amber-500 mt-2 flex-shrink-0" />
                  {gap}
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {datasets.map((dataset, i) => (
          <Card key={i} className="flex flex-col">
            <CardHeader className="pb-2 bg-gray-50/50 dark:bg-gray-800/30 border-b border-gray-100 dark:border-gray-800">
              <div className="flex justify-between items-start">
                <CardTitle className="text-lg font-bold">{dataset.name}</CardTitle>
                <ConfidenceBadge type={dataset.evidence_type || 'FACT'} />
              </div>
              <div className="flex flex-wrap gap-2 mt-2">
                {dataset.domain && <Badge variant="secondary">{dataset.domain}</Badge>}
                {dataset.size && <Badge variant="outline">{dataset.size}</Badge>}
                {dataset.data_type && <Badge variant="outline">{dataset.data_type}</Badge>}
                {dataset.availability && <Badge variant="outline" className="border-green-200 text-green-700 dark:text-green-400">{dataset.availability}</Badge>}
                {dataset.license && <Badge variant="outline" className="border-blue-200 text-blue-700 dark:text-blue-400">{dataset.license}</Badge>}
              </div>
            </CardHeader>
            <CardContent className="pt-4 flex-grow flex flex-col gap-4">
              {dataset.classes && (
                <div className="text-sm">
                  <span className="font-semibold text-gray-700 dark:text-gray-300">Classes: </span>
                  <span className="text-gray-600 dark:text-gray-400">{dataset.classes}</span>
                </div>
              )}
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {dataset.strengths && (
                  <div className="bg-green-50/50 dark:bg-green-900/10 p-3 rounded-lg border border-green-100 dark:border-green-900">
                    <h4 className="text-xs font-semibold text-green-800 dark:text-green-400 uppercase tracking-wider mb-2 flex items-center gap-1">
                      <PlusCircle className="w-3 h-3" /> Strengths
                    </h4>
                    <p className="text-sm text-gray-700 dark:text-gray-300">{dataset.strengths}</p>
                  </div>
                )}

                {dataset.limitations && (
                  <div className="bg-red-50/50 dark:bg-red-900/10 p-3 rounded-lg border border-red-100 dark:border-red-900">
                    <h4 className="text-xs font-semibold text-red-800 dark:text-red-400 uppercase tracking-wider mb-2 flex items-center gap-1">
                      <MinusCircle className="w-3 h-3" /> Limitations
                    </h4>
                    <p className="text-sm text-gray-700 dark:text-gray-300">{dataset.limitations}</p>
                  </div>
                )}
              </div>

              {dataset.common_usage && (
                <div>
                  <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Common Usage</h4>
                  <p className="text-sm text-gray-700 dark:text-gray-300">{dataset.common_usage}</p>
                </div>
              )}

              {dataset.potential_gaps && (
                <div className="bg-amber-50/50 dark:bg-amber-900/10 p-3 rounded-lg border border-amber-100 dark:border-amber-900">
                  <h4 className="text-xs font-semibold text-amber-800 dark:text-amber-400 uppercase tracking-wider mb-1 flex items-center gap-1">
                    <AlertCircle className="w-3 h-3" /> Potential Data Gap
                  </h4>
                  <p className="text-sm text-amber-900 dark:text-amber-200">{dataset.potential_gaps}</p>
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
