"use client";

import { TechnologyLandscape } from '@/types';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { ConfidenceBadge } from '@/components/ui/ConfidenceBadge';
import { Cpu, CheckCircle2, TrendingUp, FlaskConical, HelpCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

interface TechnologyTabProps {
  technologies: TechnologyLandscape | null;
}

export function TechnologyTab({ technologies }: TechnologyTabProps) {
  if (!technologies) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <Cpu className="w-12 h-12 text-gray-300 dark:text-gray-600 mb-4" />
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">No technology analysis</h3>
        <p className="text-gray-500 dark:text-gray-400 mt-2 max-w-md">
          Technology landscape analysis is not available for this project.
        </p>
      </div>
    );
  }

  const sections = [
    {
      title: 'Established Technologies',
      icon: CheckCircle2,
      data: technologies.established,
      colorClass: 'text-green-600 dark:text-green-400',
      bgClass: 'bg-green-50 dark:bg-green-900/10 border-green-100 dark:border-green-900'
    },
    {
      title: 'Emerging Technologies',
      icon: TrendingUp,
      data: technologies.emerging,
      colorClass: 'text-blue-600 dark:text-blue-400',
      bgClass: 'bg-blue-50 dark:bg-blue-900/10 border-blue-100 dark:border-blue-900'
    },
    {
      title: 'Experimental Technologies',
      icon: FlaskConical,
      data: technologies.experimental,
      colorClass: 'text-purple-600 dark:text-purple-400',
      bgClass: 'bg-purple-50 dark:bg-purple-900/10 border-purple-100 dark:border-purple-900'
    },
    {
      title: 'Potentially Relevant',
      icon: HelpCircle,
      data: technologies.potentially_relevant,
      colorClass: 'text-amber-600 dark:text-amber-400',
      bgClass: 'bg-amber-50 dark:bg-amber-900/10 border-amber-100 dark:border-amber-900'
    }
  ];

  return (
    <div className="space-y-8">
      {sections.map((section, i) => {
        if (!section.data || section.data.length === 0) return null;
        const Icon = section.icon;

        return (
          <div key={i} className="space-y-4">
            <h3 className={cn("text-lg font-bold flex items-center gap-2", section.colorClass)}>
              <Icon className="w-5 h-5" />
              {section.title}
              <span className="text-sm font-normal text-gray-500 ml-2">({section.data.length})</span>
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {section.data.map((tech, j) => (
                <Card key={j} className={cn("border transition-colors", section.bgClass)}>
                  <CardHeader className="pb-2">
                    <div className="flex justify-between items-start gap-2">
                      <CardTitle className="text-base font-semibold">{tech.name}</CardTitle>
                      <ConfidenceBadge type={tech.evidence_type || 'FACT'} />
                    </div>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-gray-700 dark:text-gray-300 mb-3">
                      {tech.description}
                    </p>
                    {tech.use_cases && tech.use_cases.length > 0 && (
                      <div>
                        <h4 className="text-xs font-semibold text-gray-500 uppercase mb-1">Use Cases</h4>
                        <ul className="text-xs text-gray-600 dark:text-gray-400 list-disc pl-4 space-y-0.5">
                          {tech.use_cases.map((uc, k) => <li key={k}>{uc}</li>)}
                        </ul>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}
