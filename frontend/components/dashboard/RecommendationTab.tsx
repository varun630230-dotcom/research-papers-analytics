"use client";

import { ProjectRecommendation } from '@/types';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { ConfidenceBadge } from '@/components/ui/ConfidenceBadge';
import { AlertTriangle, Rocket, CheckCircle, Database, Server, Settings, Cpu, Map } from 'lucide-react';
import { cn } from '@/lib/utils';

interface RecommendationTabProps {
  recommendation: ProjectRecommendation | null;
}

export function RecommendationTab({ recommendation }: RecommendationTabProps) {
  if (!recommendation) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <Map className="w-12 h-12 text-gray-300 dark:text-gray-600 mb-4" />
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">No project recommendation</h3>
        <p className="text-gray-500 dark:text-gray-400 mt-2 max-w-md">
          A comprehensive project recommendation has not been generated yet.
        </p>
      </div>
    );
  }

  const getDifficultyColor = (diff: string) => {
    switch (diff?.toLowerCase()) {
      case 'easy': return 'bg-green-100 text-green-800 border-green-200 dark:bg-green-900/30 dark:text-green-300';
      case 'medium': return 'bg-blue-100 text-blue-800 border-blue-200 dark:bg-blue-900/30 dark:text-blue-300';
      case 'hard': return 'bg-orange-100 text-orange-800 border-orange-200 dark:bg-orange-900/30 dark:text-orange-300';
      case 'expert': return 'bg-red-100 text-red-800 border-red-200 dark:bg-red-900/30 dark:text-red-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-200 dark:bg-gray-800 dark:text-gray-300';
    }
  };

  return (
    <div className="space-y-8 max-w-5xl mx-auto pb-12">
      <div className="text-center space-y-4 mb-10">
        <Badge variant="outline" className="text-blue-600 border-blue-200 bg-blue-50 dark:bg-blue-900/20 dark:border-blue-800 dark:text-blue-300">
          Synthesized Project Recommendation
        </Badge>
        <h1 className="text-4xl font-extrabold text-gray-900 dark:text-white tracking-tight">
          {recommendation.title}
        </h1>
        <div className="flex items-center justify-center gap-4 mt-4">
          <Badge className={cn("px-3 py-1 text-sm font-medium", getDifficultyColor(recommendation.development_difficulty || 'medium'))}>
            Difficulty: {recommendation.development_difficulty}
          </Badge>
          <ConfidenceBadge level="high" type="hypothesis" label="AI Generated" />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="space-y-6">
          <div>
            <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-3 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-amber-500" />
              The Problem & Current State
            </h3>
            <p className="text-sm text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-gray-800/50 p-4 rounded-lg border border-gray-100 dark:border-gray-800">
              {recommendation.problem_statement}
            </p>
            {recommendation.existing_system && (
              <p className="text-sm text-gray-700 dark:text-gray-300 mt-3 p-4">
                <span className="font-semibold block mb-1">Current Approaches:</span>
                {recommendation.existing_system}
              </p>
            )}
            {recommendation.limitations_of_existing && recommendation.limitations_of_existing.length > 0 && (
              <div className="mt-3 pl-4">
                <span className="text-sm font-semibold text-red-700 dark:text-red-400 block mb-2">Key Limitations:</span>
                <ul className="space-y-1">
                  {recommendation.limitations_of_existing.map((lim, i) => (
                    <li key={i} className="text-sm text-gray-600 dark:text-gray-400 flex items-start gap-2">
                      <span className="text-red-500 mt-0.5">•</span> {lim}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          <div>
             <h3 className="text-lg font-bold text-emerald-700 dark:text-emerald-400 mb-3 flex items-center gap-2">
                <CheckCircle className="w-5 h-5" />
                Identified Opportunity
             </h3>
             <div className="bg-emerald-50 dark:bg-emerald-900/10 p-4 rounded-lg border border-emerald-100 dark:border-emerald-900">
               <p className="text-sm text-emerald-800 dark:text-emerald-200">
                 {recommendation.identified_opportunity}
               </p>
             </div>
          </div>
        </div>

        <div className="space-y-6">
          <Card className="border-blue-200 dark:border-blue-800 bg-gradient-to-br from-white to-blue-50/50 dark:from-gray-900 dark:to-blue-900/10 h-full shadow-md">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-blue-700 dark:text-blue-400">
                <Rocket className="w-6 h-6" />
                Proposed Solution
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <p className="text-sm text-gray-700 dark:text-gray-300">
                {recommendation.proposed_solution}
              </p>
              
              <div className="bg-blue-100/50 dark:bg-blue-900/20 p-4 rounded border border-blue-200/50 dark:border-blue-800/50">
                <h4 className="text-xs font-bold uppercase tracking-wider text-blue-800 dark:text-blue-300 mb-2">Core Innovation</h4>
                <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                  {recommendation.core_innovation}
                </p>
              </div>

              {recommendation.target_users && (
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-2">Target Users</h4>
                  <p className="text-sm text-gray-700 dark:text-gray-300">
                    {recommendation.target_users}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      <div className="mt-12">
        <h2 className="text-2xl font-bold mb-6 text-gray-900 dark:text-white border-b border-gray-200 dark:border-gray-800 pb-2">
          Technical Implementation
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
           <Card>
             <CardHeader className="pb-3">
               <CardTitle className="text-sm flex items-center gap-2">
                 <Settings className="w-4 h-4 text-gray-500" /> Stack & Models
               </CardTitle>
             </CardHeader>
             <CardContent className="space-y-4">
               <div>
                 <span className="text-xs font-semibold text-gray-500 block mb-1">Tech Stack</span>
                 <div className="flex flex-wrap gap-1.5">
                   {recommendation.technology_stack?.map((t, i) => <Badge key={i} variant="outline">{t}</Badge>)}
                 </div>
               </div>
               <div>
                 <span className="text-xs font-semibold text-gray-500 block mb-1">AI Models</span>
                 <div className="flex flex-wrap gap-1.5">
                   {recommendation.ai_models?.map((m, i) => <Badge key={i} variant="secondary" className="bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300">{m}</Badge>)}
                 </div>
               </div>
             </CardContent>
           </Card>

           <Card>
             <CardHeader className="pb-3">
               <CardTitle className="text-sm flex items-center gap-2">
                 <Database className="w-4 h-4 text-gray-500" /> Data & Integration
               </CardTitle>
             </CardHeader>
             <CardContent className="space-y-4">
               <div>
                 <span className="text-xs font-semibold text-gray-500 block mb-1">Datasets</span>
                 <ul className="text-xs space-y-1 text-gray-600 dark:text-gray-400">
                   {recommendation.datasets?.map((d, i) => <li key={i}>• {d}</li>)}
                 </ul>
               </div>
               <div>
                 <span className="text-xs font-semibold text-gray-500 block mb-1">APIs</span>
                 <ul className="text-xs space-y-1 text-gray-600 dark:text-gray-400">
                   {recommendation.apis?.map((a, i) => <li key={i}>• {a}</li>)}
                 </ul>
               </div>
               {recommendation.database && (
                 <div>
                   <span className="text-xs font-semibold text-gray-500 block mb-1">Database Strategy</span>
                   <p className="text-xs text-gray-600 dark:text-gray-400">{recommendation.database}</p>
                 </div>
               )}
             </CardContent>
           </Card>

           <Card>
             <CardHeader className="pb-3">
               <CardTitle className="text-sm flex items-center gap-2">
                 <Server className="w-4 h-4 text-gray-500" /> Deployment & Evaluation
               </CardTitle>
             </CardHeader>
             <CardContent className="space-y-4">
               {recommendation.deployment_strategy && (
                 <div>
                   <span className="text-xs font-semibold text-gray-500 block mb-1">Deployment Strategy</span>
                   <p className="text-xs text-gray-600 dark:text-gray-400">{recommendation.deployment_strategy}</p>
                 </div>
               )}
               <div>
                 <span className="text-xs font-semibold text-gray-500 block mb-1">Evaluation Metrics</span>
                 <ul className="text-xs space-y-1 text-gray-600 dark:text-gray-400">
                   {recommendation.evaluation_metrics?.map((m, i) => <li key={i}>• {m}</li>)}
                 </ul>
               </div>
             </CardContent>
           </Card>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-12">
        <div>
           <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4">Key Features</h3>
           <ol className="space-y-3">
             {recommendation.key_features?.map((feature, i) => (
               <li key={i} className="flex gap-3">
                 <span className="w-6 h-6 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5">
                   {i + 1}
                 </span>
                 <span className="text-sm text-gray-700 dark:text-gray-300">{feature}</span>
               </li>
             ))}
           </ol>
        </div>

        <div className="space-y-6">
           {recommendation.risks && recommendation.risks.length > 0 && (
             <div className="bg-amber-50 dark:bg-amber-900/10 p-4 rounded-lg border border-amber-100 dark:border-amber-900">
               <h3 className="text-sm font-bold text-amber-900 dark:text-amber-400 mb-2 flex items-center gap-2">
                 <AlertTriangle className="w-4 h-4" /> Implementation Risks
               </h3>
               <ul className="space-y-1.5">
                 {recommendation.risks.map((risk, i) => (
                   <li key={i} className="text-sm text-amber-800 dark:text-amber-200/80 flex items-start gap-2">
                     <span className="mt-0.5">•</span> {risk}
                   </li>
                 ))}
               </ul>
             </div>
           )}

           <div className="bg-gray-50 dark:bg-gray-800/50 p-4 rounded-lg border border-gray-100 dark:border-gray-800">
              <h3 className="text-sm font-bold text-gray-900 dark:text-gray-100 mb-2">Expected Outcome</h3>
              <p className="text-sm text-gray-700 dark:text-gray-300">
                {recommendation.expected_outcome}
              </p>
           </div>
        </div>
      </div>
    </div>
  );
}
