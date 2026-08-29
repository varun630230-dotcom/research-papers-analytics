"use client";

import { MarketGap } from '@/types';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { ConfidenceBadge } from '@/components/ui/ConfidenceBadge';
import { Badge } from '@/components/ui/Badge';
import { TrendingUp, Users, Target, Lightbulb, ShoppingBag, ShieldAlert, CheckCircle2 } from 'lucide-react';

interface MarketGapsTabProps {
  gaps: MarketGap[];
}

export function MarketGapsTab({ gaps = [] }: MarketGapsTabProps) {
  if (!gaps || gaps.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <ShoppingBag className="w-12 h-12 text-gray-300 dark:text-gray-600 mb-4" />
        <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100">No Market Gaps Recorded</h3>
        <p className="text-gray-500 dark:text-gray-400 mt-2 max-w-md text-sm">
          No product or commercial market gaps identified.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Context Banner */}
      <div className="bg-gradient-to-r from-indigo-50 to-blue-50 dark:from-gray-900 dark:to-gray-850 border border-indigo-100 dark:border-gray-800 p-5 rounded-2xl flex items-start gap-3.5 shadow-sm">
        <ShoppingBag className="w-5 h-5 text-indigo-600 dark:text-indigo-400 mt-0.5 shrink-0" />
        <div className="space-y-1 text-xs sm:text-sm">
          <strong className="text-gray-900 dark:text-gray-100 font-bold block">
            Product & Commercial Market Gap Intelligence
          </strong>
          <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
            These gaps represent unmet commercial user needs, cost barriers, privacy limitations, and operational bottlenecks separated from academic algorithm limitations.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {gaps.map((gap, i) => (
          <Card key={i} className="bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-800 flex flex-col h-full shadow-sm hover:shadow-md transition">
            <CardHeader className="pb-3 border-b border-gray-100 dark:border-gray-800">
              <div className="flex justify-between items-start gap-4">
                <div className="space-y-2">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="px-2.5 py-0.5 rounded-md text-xs font-bold bg-indigo-50 text-indigo-700 dark:bg-indigo-950/50 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800">
                      {gap.type || 'Market Gap'}
                    </span>
                    <ConfidenceBadge type={gap.confidence || 'Medium'} />
                  </div>
                  <CardTitle className="text-lg font-bold text-gray-900 dark:text-gray-100 leading-tight">
                    {gap.problem}
                  </CardTitle>
                </div>
              </div>
            </CardHeader>
            
            <CardContent className="p-6 flex-grow flex flex-col gap-4 text-xs">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {gap.affected_users && (
                  <div>
                    <strong className="text-gray-500 uppercase tracking-wider mb-1 flex items-center gap-1.5 font-bold">
                      <Users className="w-3.5 h-3.5" /> Affected Users:
                    </strong>
                    <p className="text-gray-800 dark:text-gray-200">{gap.affected_users}</p>
                  </div>
                )}
                
                <div>
                  <strong className="text-gray-500 uppercase tracking-wider mb-1 flex items-center gap-1.5 font-bold">
                    <Target className="w-3.5 h-3.5" /> Validation Status:
                  </strong>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-amber-700 dark:text-amber-300 border border-amber-300 dark:border-amber-800 px-2 py-0.5 rounded bg-amber-50 dark:bg-amber-950/40 font-semibold">
                      Needs Field Validation
                    </span>
                  </div>
                </div>
              </div>

              <div className="space-y-3">
                <div className="bg-gray-50 dark:bg-gray-800/50 p-3.5 rounded-xl border border-gray-200 dark:border-gray-800 space-y-1.5">
                  <strong className="text-gray-900 dark:text-gray-100 font-bold block">Current Market Solutions & Limitations:</strong>
                  <p className="text-gray-700 dark:text-gray-300">
                    {gap.current_limitations || 'No limitations specified.'}
                  </p>
                  {gap.current_solutions && (
                    <div className="text-[11px] text-gray-500 dark:text-gray-400 pt-1 border-t border-gray-200 dark:border-gray-700">
                      <strong>Existing solutions:</strong> {gap.current_solutions}
                    </div>
                  )}
                  {gap.missing_capability && (
                    <div className="text-[11px] text-purple-700 dark:text-purple-300 pt-1">
                      <strong>Missing Capability:</strong> {gap.missing_capability}
                    </div>
                  )}
                </div>

                <div className="bg-emerald-50/70 dark:bg-emerald-950/30 p-3.5 rounded-xl border border-emerald-200 dark:border-emerald-800/50 space-y-1">
                  <strong className="text-emerald-900 dark:text-emerald-300 font-bold block flex items-center gap-1.5">
                    <Lightbulb className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
                    Market Opportunity:
                  </strong>
                  <p className="text-emerald-800 dark:text-emerald-200 leading-relaxed font-medium">
                    {gap.potential_opportunity}
                  </p>
                </div>
              </div>

              {gap.validation_required && (
                <div className="bg-blue-50/50 dark:bg-blue-950/20 p-3 rounded-lg border border-blue-100 dark:border-blue-900/30 text-[11px] text-blue-900 dark:text-blue-300">
                  <strong>Validation Requirement:</strong> {gap.validation_required}
                </div>
              )}

              {gap.evidence && (
                <div className="mt-auto pt-3 border-t border-gray-100 dark:border-gray-800 text-[11px] text-gray-500 dark:text-gray-400 italic">
                  <strong>Evidence Basis:</strong> {gap.evidence}
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
