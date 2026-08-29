"use client";

import { Architecture } from '@/types';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Box, ArrowRight, Layers, Database, Cpu, Monitor, Globe } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ArchitectureTabProps {
  architecture: Architecture | null;
}

export function ArchitectureTab({ architecture }: ArchitectureTabProps) {
  if (!architecture) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <Layers className="w-12 h-12 text-gray-300 dark:text-gray-600 mb-4" />
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">No architecture generated</h3>
        <p className="text-gray-500 dark:text-gray-400 mt-2 max-w-md">
          System architecture diagrams are not available for this project.
        </p>
      </div>
    );
  }

  const getIconForComponent = (name: string) => {
    const lowerName = name.toLowerCase();
    if (lowerName.includes('frontend') || lowerName.includes('ui') || lowerName.includes('client')) return Monitor;
    if (lowerName.includes('api') || lowerName.includes('backend') || lowerName.includes('server')) return Globe;
    if (lowerName.includes('database') || lowerName.includes('storage') || lowerName.includes('cache')) return Database;
    if (lowerName.includes('model') || lowerName.includes('ai') || lowerName.includes('ml') || lowerName.includes('engine')) return Cpu;
    return Box;
  };

  return (
    <div className="space-y-8">
      {architecture.diagram_description && (
        <Card className="bg-gray-900 text-gray-100 dark:bg-black dark:border-gray-800">
          <CardHeader className="pb-3 border-b border-gray-800">
            <CardTitle className="text-sm font-medium text-gray-400 uppercase tracking-wider flex items-center gap-2">
              <Layers className="w-4 h-4" /> Architecture Overview
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-4">
            <pre className="font-mono text-sm whitespace-pre-wrap overflow-x-auto text-blue-300">
              {architecture.diagram_description}
            </pre>
          </CardContent>
        </Card>
      )}

      {/* CSS-based Architecture Visualization */}
      <div className="hidden md:block bg-gray-50 dark:bg-gray-900/50 p-8 rounded-xl border border-gray-200 dark:border-gray-800">
        <h3 className="text-lg font-bold mb-8 text-center text-gray-700 dark:text-gray-300">System Flow Visualization</h3>
        
        <div className="flex flex-col items-center max-w-3xl mx-auto">
          {architecture.components?.map((comp, i) => {
            const Icon = getIconForComponent(comp.name);
            const isLast = i === (architecture.components?.length || 0) - 1;
            
            return (
              <div key={i} className="flex flex-col items-center w-full">
                <div className="w-full md:w-2/3 bg-white dark:bg-gray-800 p-4 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 relative z-10 hover:shadow-md transition-shadow">
                  <div className="flex items-start gap-4">
                    <div className="p-3 bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 rounded-lg">
                      <Icon className="w-6 h-6" />
                    </div>
                    <div className="flex-grow">
                      <h4 className="font-bold text-gray-900 dark:text-gray-100">{comp.name}</h4>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{comp.description}</p>
                      {comp.technology && (
                        <span className="inline-block mt-2 text-[10px] font-semibold bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 px-2 py-0.5 rounded">
                          {comp.technology}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                
                {!isLast && (
                  <div className="h-12 w-0.5 bg-blue-200 dark:bg-blue-800 relative z-0">
                    <ArrowRight className="w-4 h-4 text-blue-400 dark:text-blue-600 absolute -bottom-2 -left-[7px] transform rotate-90" />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div>
          <h3 className="text-xl font-bold mb-4 text-gray-900 dark:text-gray-100">Components Detail</h3>
          <div className="space-y-4">
            {architecture.components?.map((comp, i) => (
              <Card key={i}>
                <CardHeader className="pb-2">
                  <CardTitle className="text-base flex items-center justify-between">
                    <span>{comp.name}</span>
                    {comp.technology && (
                      <span className="text-xs font-normal bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">
                        {comp.technology}
                      </span>
                    )}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-700 dark:text-gray-300">{comp.description}</p>
                  {comp.connections && comp.connections.length > 0 && (
                    <div className="mt-3 text-xs text-gray-500">
                      <span className="font-semibold text-gray-700 dark:text-gray-300">Connects to: </span>
                      {comp.connections.join(', ')}
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        <div>
          <h3 className="text-xl font-bold mb-4 text-gray-900 dark:text-gray-100">Data Flow</h3>
          <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-6 shadow-sm">
            <ol className="relative border-l border-gray-200 dark:border-gray-700 ml-3">
              {architecture.data_flow?.map((step, i) => (
                <li key={i} className="mb-6 ml-6 last:mb-0">
                  <span className="absolute flex items-center justify-center w-6 h-6 bg-blue-100 rounded-full -left-3 ring-4 ring-white dark:ring-gray-950 dark:bg-blue-900 text-blue-800 dark:text-blue-300 text-xs font-bold">
                    {i + 1}
                  </span>
                  <p className="text-sm text-gray-700 dark:text-gray-300 pt-0.5">{step}</p>
                </li>
              ))}
            </ol>
          </div>
        </div>
      </div>
    </div>
  );
}
