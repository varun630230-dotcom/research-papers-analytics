"use client";

import { ExistingSolution } from '@/types';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { ConfidenceBadge } from '@/components/ui/ConfidenceBadge';
import { Badge } from '@/components/ui/Badge';
import { Layers, PlusCircle, MinusCircle, AlertCircle } from 'lucide-react';

interface ExistingSolutionsTabProps {
  solutions: ExistingSolution[];
}

export function ExistingSolutionsTab({ solutions }: ExistingSolutionsTabProps) {
  if (!solutions || solutions.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <Layers className="w-12 h-12 text-gray-300 dark:text-gray-600 mb-4" />
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">No existing solutions</h3>
        <p className="text-gray-500 dark:text-gray-400 mt-2 max-w-md">
          No existing solutions were identified from the analyzed sources.
        </p>
      </div>
    );
  }

  // Group solutions by type
  const grouped = solutions.reduce((acc, curr) => {
    const type = curr.type || 'Other';
    if (!acc[type]) acc[type] = [];
    acc[type].push(curr);
    return acc;
  }, {} as Record<string, ExistingSolution[]>);

  const getTypeColor = (type: string) => {
    switch(type.toLowerCase()) {
      case 'academic': return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300';
      case 'open-source': return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300';
      case 'commercial': return 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300';
      case 'prototype': return 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300';
    }
  };

  return (
    <div className="space-y-8">
      {Object.entries(grouped).map(([type, typeSolutions]) => (
        <div key={type} className="space-y-4">
          <h3 className="text-lg font-bold flex items-center gap-2 capitalize">
            {type} Solutions
            <span className="text-sm font-normal text-gray-500">({typeSolutions.length})</span>
          </h3>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {typeSolutions.map((solution, i) => (
              <Card key={i} className="flex flex-col">
                <CardHeader className="pb-2 border-b border-gray-100 dark:border-gray-800">
                  <div className="flex justify-between items-start gap-2">
                    <div className="space-y-1.5">
                      <CardTitle className="text-lg">{solution.name}</CardTitle>
                      <Badge className={getTypeColor(solution.type || 'other')} variant="secondary">
                        {solution.type}
                      </Badge>
                    </div>
                    <ConfidenceBadge level={solution.evidence_type as any || 'medium'} type="fact" />
                  </div>
                </CardHeader>
                <CardContent className="pt-4 flex-grow flex flex-col gap-4">
                  {solution.target_users && (
                    <div>
                      <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Target Users</h4>
                      <p className="text-sm text-gray-700 dark:text-gray-300">{solution.target_users}</p>
                    </div>
                  )}

                  {solution.main_features && solution.main_features.length > 0 && (
                    <div>
                      <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Main Features</h4>
                      <div className="flex flex-wrap gap-1.5">
                        {solution.main_features.map((feature, j) => (
                          <span key={j} className="bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 px-2 py-0.5 rounded text-xs border border-gray-200 dark:border-gray-700">
                            {feature}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {solution.technology && (
                    <div>
                      <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Technology</h4>
                      <p className="text-sm text-gray-700 dark:text-gray-300">{solution.technology}</p>
                    </div>
                  )}

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-auto">
                    {solution.strengths && solution.strengths.length > 0 && (
                      <div>
                        <h4 className="text-xs font-semibold text-green-700 dark:text-green-400 uppercase tracking-wider mb-1 flex items-center gap-1">
                          <PlusCircle className="w-3 h-3" /> Strengths
                        </h4>
                        <ul className="text-sm space-y-1">
                          {solution.strengths.map((s, j) => (
                            <li key={j} className="text-gray-600 dark:text-gray-400 pl-3 relative before:content-['•'] before:absolute before:left-0 before:text-green-500">{s}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {solution.weaknesses && solution.weaknesses.length > 0 && (
                      <div>
                        <h4 className="text-xs font-semibold text-red-700 dark:text-red-400 uppercase tracking-wider mb-1 flex items-center gap-1">
                          <MinusCircle className="w-3 h-3" /> Weaknesses
                        </h4>
                        <ul className="text-sm space-y-1">
                          {solution.weaknesses.map((w, j) => (
                            <li key={j} className="text-gray-600 dark:text-gray-400 pl-3 relative before:content-['•'] before:absolute before:left-0 before:text-red-500">{w}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>

                  {solution.missing_features && solution.missing_features.length > 0 && (
                    <div className="bg-amber-50 dark:bg-amber-900/10 p-3 rounded-lg border border-amber-100 dark:border-amber-900">
                      <h4 className="text-xs font-semibold text-amber-800 dark:text-amber-400 uppercase tracking-wider mb-1 flex items-center gap-1">
                        <AlertCircle className="w-3 h-3" /> Missing Features (Opportunities)
                      </h4>
                      <ul className="text-sm space-y-1">
                        {solution.missing_features.map((m, j) => (
                          <li key={j} className="text-amber-900 dark:text-amber-200 pl-3 relative before:content-['•'] before:absolute before:left-0 before:text-amber-500">{m}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {solution.source && (
                    <div className="text-xs text-gray-500 mt-2">
                      Source: {solution.source}
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
