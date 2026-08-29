"use client";

import { NoveltyAssessment } from '@/types';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { ConfidenceBadge } from '@/components/ui/ConfidenceBadge';
import { Award, AlertTriangle, Lightbulb, Compass, Zap } from 'lucide-react';
import { cn } from '@/lib/utils';

interface NoveltyTabProps {
  novelty: NoveltyAssessment | null;
}

export function NoveltyTab({ novelty }: NoveltyTabProps) {
  if (!novelty) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <Award className="w-12 h-12 text-gray-300 dark:text-gray-600 mb-4" />
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">No novelty assessment</h3>
        <p className="text-gray-500 dark:text-gray-400 mt-2 max-w-md">
          Novelty assessment is not available for this project yet.
        </p>
      </div>
    );
  }

  const getScoreColor = (score: string | number) => {
    if (typeof score === 'string') {
      const s = score.toLowerCase();
      if (s.includes('low')) return 'text-emerald-500 dark:text-emerald-400';
      if (s.includes('mod')) return 'text-blue-500 dark:text-blue-400';
      if (s.includes('high')) return 'text-amber-500 dark:text-amber-400';
      const num = parseInt(score, 10);
      if (!isNaN(num)) {
        if (num >= 80) return 'text-emerald-500 dark:text-emerald-400';
        if (num >= 60) return 'text-blue-500 dark:text-blue-400';
        if (num >= 40) return 'text-amber-500 dark:text-amber-400';
        return 'text-red-500 dark:text-red-400';
      }
      return 'text-blue-500 dark:text-blue-400';
    }
    if (score >= 80) return 'text-emerald-500 dark:text-emerald-400';
    if (score >= 60) return 'text-blue-500 dark:text-blue-400';
    if (score >= 40) return 'text-amber-500 dark:text-amber-400';
    return 'text-red-500 dark:text-red-400';
  };

  const getNoveltyLevelColor = (level: string) => {
    switch (level?.toLowerCase()) {
      case 'high': return 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-300 border-emerald-200';
      case 'medium': return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300 border-blue-200';
      case 'low': return 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300 border-amber-200';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300 border-gray-200';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-end">
        <ConfidenceBadge level="high" type="inference" label="Assessment Confidence" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="md:col-span-1 flex flex-col items-center justify-center text-center p-6 bg-gradient-to-b from-white to-gray-50 dark:from-gray-900 dark:to-gray-900/80">
          <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">Similarity Score</h3>
          <div className={cn("text-5xl font-bold mb-2", getScoreColor(novelty.similarity_score || ''))}>
            {novelty.similarity_score}
          </div>
          <p className="text-sm text-gray-500 max-w-[200px]">
            Lower score indicates higher novelty.
          </p>
        </Card>

        <Card className="md:col-span-2">
          <CardContent className="p-6 h-full flex flex-col justify-center space-y-4">
            <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 flex items-center gap-2">
              <Award className="w-6 h-6 text-indigo-500" />
              Final Assessment
            </h3>
            <blockquote className="text-lg italic text-gray-700 dark:text-gray-300 border-l-4 border-indigo-500 pl-4">
              "{novelty.final_assessment}"
            </blockquote>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="border-blue-100 dark:border-blue-900/50">
          <CardHeader className="bg-blue-50/50 dark:bg-blue-900/10 pb-4">
            <CardTitle className="text-blue-900 dark:text-blue-300 flex items-center gap-2">
              <Zap className="w-5 h-5 text-blue-500" /> Unique Aspects
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-4">
            <ul className="space-y-2">
              {novelty.unique_aspects?.map((aspect, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="text-blue-500 mt-1">•</span>
                  <span className="text-gray-700 dark:text-gray-300 text-sm">{aspect}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>

        <Card className="border-amber-100 dark:border-amber-900/50">
          <CardHeader className="bg-amber-50/50 dark:bg-amber-900/10 pb-4">
            <CardTitle className="text-amber-900 dark:text-amber-300 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-amber-500" /> Common Approaches (To Avoid)
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-4">
            <ul className="space-y-2">
              {novelty.common_approaches?.map((approach, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="text-amber-500 mt-1">•</span>
                  <span className="text-gray-700 dark:text-gray-300 text-sm">{approach}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {novelty.potential_differentiators && novelty.potential_differentiators.length > 0 && (
          <Card className="border-emerald-100 dark:border-emerald-900/50">
            <CardHeader className="bg-emerald-50/50 dark:bg-emerald-900/10 pb-4">
              <CardTitle className="text-emerald-900 dark:text-emerald-300 flex items-center gap-2">
                <Lightbulb className="w-5 h-5 text-emerald-500" /> Potential Differentiators
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-4">
              <ul className="space-y-2">
                {novelty.potential_differentiators.map((diff, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-gray-700 dark:text-gray-300">
                    <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-1.5 flex-shrink-0" />
                    {diff}
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        )}

        {novelty.innovation_directions && novelty.innovation_directions.length > 0 && (
          <Card className="border-purple-100 dark:border-purple-900/50">
            <CardHeader className="bg-purple-50/50 dark:bg-purple-900/10 pb-4">
              <CardTitle className="text-purple-900 dark:text-purple-300 flex items-center gap-2">
                <Compass className="w-5 h-5 text-purple-500" /> Innovation Directions
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-4">
              <ul className="space-y-2">
                {novelty.innovation_directions.map((dir, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-gray-700 dark:text-gray-300">
                    <div className="w-1.5 h-1.5 rounded-full bg-purple-500 mt-1.5 flex-shrink-0" />
                    {dir}
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        )}
      </div>

      {novelty.overcrowded_areas && novelty.overcrowded_areas.length > 0 && (
        <div className="bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500 p-4 rounded-r">
          <h4 className="text-sm font-bold text-red-900 dark:text-red-300 mb-2 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4" /> Overcrowded Areas Detected
          </h4>
          <p className="text-sm text-red-800 dark:text-red-200">
            The following areas are heavily saturated in current research. Consider pivoting away from: <strong>{novelty.overcrowded_areas.join(', ')}</strong>.
          </p>
        </div>
      )}

      {novelty.component_assessments && novelty.component_assessments.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Component-Level Novelty Assessment</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead className="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-800 dark:text-gray-300">
                  <tr>
                    <th className="px-4 py-3 rounded-tl-lg">Component</th>
                    <th className="px-4 py-3">Novelty Level</th>
                    <th className="px-4 py-3 rounded-tr-lg">Explanation</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 dark:divide-gray-800">
                  {novelty.component_assessments.map((comp, i) => (
                    <tr key={i} className="bg-white dark:bg-gray-900">
                      <td className="px-4 py-3 font-medium text-gray-900 dark:text-white align-top">
                        {comp.component}
                      </td>
                      <td className="px-4 py-3 align-top whitespace-nowrap">
                        <span className={cn("px-2.5 py-1 rounded-full text-xs font-semibold border", getNoveltyLevelColor(comp.novelty_level))}>
                          {comp.novelty_level}
                        </span>
                      </td>
                      <td className="px-4 py-3 align-top text-gray-600 dark:text-gray-400">
                        {comp.explanation}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="text-xs text-center text-gray-500 mt-8">
        Disclaimer: This novelty assessment compares your idea against the retrieved research context. It does not guarantee patentability or absence of prior art globally.
      </div>
    </div>
  );
}
