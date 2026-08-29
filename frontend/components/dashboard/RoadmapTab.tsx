"use client";

import { RoadmapPhase } from '@/types';
import { Card, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Calendar, Clock, CheckCircle2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface RoadmapTabProps {
  roadmap: RoadmapPhase[];
}

export function RoadmapTab({ roadmap }: RoadmapTabProps) {
  if (!roadmap || roadmap.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <Calendar className="w-12 h-12 text-gray-300 dark:text-gray-600 mb-4" />
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">No roadmap generated</h3>
        <p className="text-gray-500 dark:text-gray-400 mt-2 max-w-md">
          Development roadmap is not available for this project.
        </p>
      </div>
    );
  }

  const getComplexityColor = (complexity: string) => {
    switch (complexity?.toLowerCase()) {
      case 'easy': return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300 border-green-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300 border-yellow-200';
      case 'hard': return 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300 border-orange-200';
      case 'advanced': return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300 border-red-200';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300 border-gray-200';
    }
  };

  const totalDuration = roadmap.reduce((acc, phase) => {
    // Very rough heuristic to extract number of weeks from strings like "2-3 weeks" or "1 month"
    const weeksMatch = phase.estimated_duration?.match(/(\d+)/);
    if (weeksMatch) {
       const num = parseInt(weeksMatch[1], 10);
       if (phase.estimated_duration?.toLowerCase().includes('month')) return acc + num * 4;
       return acc + num;
    }
    return acc;
  }, 0);

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      <div className="flex justify-between items-center bg-gray-50 dark:bg-gray-800/50 p-4 rounded-xl border border-gray-200 dark:border-gray-700">
        <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100 flex items-center gap-2">
           <Calendar className="w-5 h-5 text-blue-500" /> Development Roadmap
        </h2>
        {totalDuration > 0 && (
          <div className="text-sm text-gray-600 dark:text-gray-400 flex items-center gap-1.5">
             <Clock className="w-4 h-4" />
             Estimated Total: ~{totalDuration} weeks
          </div>
        )}
      </div>

      <div className="relative border-l-2 border-gray-200 dark:border-gray-800 ml-4 md:ml-6 space-y-12">
        {roadmap.map((phase, i) => (
          <div key={i} className="relative pl-8 md:pl-10">
            {/* Phase Node */}
            <div className="absolute -left-[17px] top-0 bg-white dark:bg-gray-950 p-1 rounded-full">
              <div className="w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center text-xs font-bold shadow-md ring-4 ring-white dark:ring-gray-950">
                {phase.phase_number || (i + 1)}
              </div>
            </div>

            <Card className="hover:shadow-md transition-shadow border-gray-200 dark:border-gray-800">
              <CardContent className="p-6">
                <div className="flex flex-col md:flex-row md:justify-between md:items-start gap-4 mb-4">
                  <div>
                    <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100">{phase.title}</h3>
                    {phase.estimated_duration && (
                      <p className="text-sm text-gray-500 flex items-center gap-1.5 mt-1">
                        <Clock className="w-3.5 h-3.5" /> {phase.estimated_duration}
                      </p>
                    )}
                  </div>
                  <Badge variant="outline" className={cn("px-2.5 py-1 text-xs font-medium whitespace-nowrap", getComplexityColor(phase.complexity))}>
                    Complexity: {phase.complexity || 'Unknown'}
                  </Badge>
                </div>

                {phase.tasks && phase.tasks.length > 0 && (
                  <div className="bg-gray-50 dark:bg-gray-900/50 p-4 rounded-lg">
                    <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Key Tasks</h4>
                    <ul className="space-y-2">
                      {phase.tasks.map((task, j) => (
                        <li key={j} className="flex items-start gap-2.5 text-sm text-gray-700 dark:text-gray-300">
                          <CheckCircle2 className="w-4 h-4 text-gray-300 dark:text-gray-600 mt-0.5 flex-shrink-0" />
                          <span>{task}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        ))}
      </div>
    </div>
  );
}
