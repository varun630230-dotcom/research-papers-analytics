"use client";

import { Opportunity } from '@/types';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { ConfidenceBadge } from '@/components/ui/ConfidenceBadge';
import { ScoreGauge } from '@/components/ui/ScoreGauge';
import { Badge } from '@/components/ui/Badge';
import { Rocket, Target, Zap, Activity, Info, CheckCircle2, ShieldCheck, Database, Sliders } from 'lucide-react';
import { OpportunityRadar } from '@/components/charts/OpportunityRadar';

interface OpportunitiesTabProps {
  opportunities: Opportunity[];
}

export function OpportunitiesTab({ opportunities = [] }: OpportunitiesTabProps) {
  if (!opportunities || opportunities.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <Rocket className="w-12 h-12 text-gray-300 dark:text-gray-600 mb-4" />
        <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100">No Opportunities Formulated</h3>
        <p className="text-gray-500 dark:text-gray-400 mt-2 max-w-md text-sm">
          Not enough synthesized gap data to formulate verified innovation opportunities.
        </p>
      </div>
    );
  }

  const sortedOpps = [...opportunities].sort((a, b) => 
    (b.scores?.overall || 0) - (a.scores?.overall || 0)
  );

  return (
    <div className="space-y-8">
      {/* Transparency Disclaimer */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-gray-900 dark:to-gray-850 border border-blue-100 dark:border-gray-800 p-5 rounded-2xl flex items-start gap-3.5 shadow-sm">
        <Sliders className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5 shrink-0" />
        <div className="space-y-1 text-xs sm:text-sm">
          <strong className="text-gray-900 dark:text-gray-100 font-bold block">
            Transparent Weighted Prioritization Model
          </strong>
          <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
            Overall Opportunity Score formula: <strong>Research Gap Strength (30%)</strong> + <strong>Market Evidence (20%)</strong> + <strong>Technology Feasibility (20%)</strong> + <strong>Data Availability (10%)</strong> + <strong>Differentiation Potential (10%)</strong> + <strong>Evidence Confidence (10%)</strong>.
          </p>
          <p className="text-[11px] text-gray-400 italic">
            *AI-assisted opportunity prioritization based on empirical literature and market signals; not an objective financial valuation.
          </p>
        </div>
      </div>

      <div className="space-y-12">
        {sortedOpps.map((opp, i) => (
          <div key={i} className="space-y-6">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-blue-600 text-white font-extrabold text-sm flex items-center justify-center shadow-sm shrink-0">
                {i + 1}
              </div>
              <h2 className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-gray-100 leading-tight">
                {opp.title}
              </h2>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 space-y-6">
                <Card className="bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-800 shadow-sm">
                  <CardContent className="p-6 space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                      <div className="space-y-3 text-xs">
                        <h4 className="text-xs font-bold text-gray-900 dark:text-gray-100 uppercase tracking-wider flex items-center gap-1.5">
                          <Target className="w-4 h-4 text-purple-600" />
                          The Problem & Existing State
                        </h4>
                        <div className="space-y-2">
                          <p className="text-gray-700 dark:text-gray-300"><strong className="text-gray-900 dark:text-gray-100">Problem:</strong> {opp.problem}</p>
                          <p className="text-gray-700 dark:text-gray-300"><strong className="text-gray-900 dark:text-gray-100">Existing Situation:</strong> {opp.existing_situation}</p>
                          <div className="bg-purple-50 dark:bg-purple-950/30 p-2.5 rounded-lg border border-purple-100 dark:border-purple-900/50">
                            <strong className="text-purple-900 dark:text-purple-300 font-bold block mb-0.5">Identified Gap:</strong>
                            <span className="text-purple-800 dark:text-purple-200">{opp.identified_gap}</span>
                          </div>
                        </div>
                      </div>
                      
                      <div className="bg-blue-50/70 dark:bg-blue-950/20 p-4 rounded-xl border border-blue-100 dark:border-blue-900/40 flex flex-col justify-between text-xs space-y-3">
                        <div>
                          <h4 className="text-xs font-bold text-blue-900 dark:text-blue-300 uppercase tracking-wider flex items-center gap-1.5 mb-2">
                            <Zap className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                            Proposed Innovation
                          </h4>
                          <p className="text-blue-950 dark:text-blue-100 leading-relaxed font-medium">
                            {opp.proposed_innovation}
                          </p>
                        </div>
                        
                        <div className="pt-3 border-t border-blue-200/50 dark:border-blue-900/50 space-y-1">
                          <span className="text-[10px] font-bold uppercase text-blue-700 dark:text-blue-400">Potential Impact</span>
                          <p className="text-xs font-semibold text-blue-900 dark:text-blue-200">{opp.potential_impact}</p>
                        </div>
                      </div>
                    </div>

                    {/* Data Requirements & Differentiation */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t border-gray-100 dark:border-gray-800 text-xs">
                      <div>
                        <strong className="text-gray-900 dark:text-gray-100 font-bold block mb-1 flex items-center gap-1.5">
                          <Database className="w-3.5 h-3.5 text-indigo-500" />
                          Data & Benchmark Requirements:
                        </strong>
                        <p className="text-gray-600 dark:text-gray-400">
                          {opp.data_requirements || 'Domain-specific labeled validation benchmarks and multi-turn text.'}
                        </p>
                      </div>
                      <div>
                        <strong className="text-gray-900 dark:text-gray-100 font-bold block mb-1 flex items-center gap-1.5">
                          <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" />
                          Differentiation Assessment:
                        </strong>
                        <p className="text-gray-600 dark:text-gray-400">
                          {opp.differentiation_potential || 'Moderate to high differentiation from generic cloud baselines.'}
                        </p>
                      </div>
                    </div>

                    {/* Required Technologies */}
                    <div className="pt-4 border-t border-gray-100 dark:border-gray-800 space-y-2">
                      <h4 className="text-xs font-bold text-gray-900 dark:text-gray-100 uppercase tracking-wider">
                        Required Technology Stack
                      </h4>
                      <div className="flex flex-wrap gap-1.5">
                        {opp.required_technologies?.map((tech, j) => (
                          <span key={j} className="bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 px-2.5 py-1 rounded-md text-xs font-medium border border-gray-200 dark:border-gray-700">
                            {tech}
                          </span>
                        ))}
                      </div>
                    </div>
                    
                    {/* Validation Steps */}
                    <div className="pt-4 border-t border-gray-100 dark:border-gray-800 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 text-xs">
                      <div className="space-y-1.5">
                        <strong className="text-gray-900 dark:text-gray-100 font-bold block">
                          Experimental Validation Roadmap:
                        </strong>
                        <ul className="space-y-1 text-gray-600 dark:text-gray-400 list-disc pl-4">
                          {opp.validation_steps?.map((step, j) => <li key={j}>{step}</li>)}
                        </ul>
                      </div>
                      <div className="shrink-0 self-end sm:self-center">
                        <ConfidenceBadge type={opp.evidence_level || 'Evidence-backed'} />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Score Radar & Gauge */}
              {opp.scores && (
                <div className="space-y-5">
                  <Card className="bg-gradient-to-br from-gray-900 to-gray-950 text-white border-gray-800 shadow-md">
                    <CardContent className="p-6 flex flex-col items-center">
                      <div className="w-44 h-44 flex items-center justify-center">
                        <ScoreGauge 
                          score={opp.scores.overall || 0} 
                          label="Weighted Score" 
                        />
                      </div>
                      <p className="text-center text-xs text-gray-400 mt-2">
                        {opp.scores.weighting_explanation || 'Research: 30% | Market: 20% | Tech: 20% | Data: 10% | Diff: 10% | Evidence: 10%'}
                      </p>
                    </CardContent>
                  </Card>
                  
                  <Card className="bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-800 shadow-sm">
                    <CardHeader className="pb-2">
                      <CardTitle className="text-xs font-bold text-gray-900 dark:text-gray-100 uppercase tracking-wider flex items-center gap-2">
                        <Activity className="w-4 h-4 text-blue-600" /> Multi-Dimensional Radar
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="p-3">
                      <div className="h-60 -ml-2">
                        <OpportunityRadar scores={opp.scores} />
                      </div>
                    </CardContent>
                  </Card>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
