import React from 'react'
import { AnalysisProgress } from '@/types'
import { Check, Loader2, X, BrainCircuit, Search, Database, FileText, Layers, TrendingUp, Lightbulb, Zap, Code, ShieldAlert, BookOpen } from 'lucide-react'

interface AnalysisPipelineProps {
  progress: AnalysisProgress
}

const DEFAULT_STAGES = [
  { name: 'Understanding your idea', icon: BrainCircuit },
  { name: 'Expanding research queries', icon: Search },
  { name: 'Searching academic sources', icon: BookOpen },
  { name: 'Identifying existing methods', icon: Layers },
  { name: 'Analyzing datasets', icon: Database },
  { name: 'Exploring technologies', icon: Code },
  { name: 'Mapping existing solutions', icon: FileText },
  { name: 'Extracting limitations', icon: ShieldAlert },
  { name: 'Detecting potential gaps', icon: TrendingUp },
  { name: 'Evaluating opportunities', icon: Lightbulb },
  { name: 'Designing recommended solution', icon: Zap },
]

export function AnalysisPipeline({ progress }: AnalysisPipelineProps) {
  const percentComplete = progress.total_stages > 0 
    ? Math.round((progress.current_stage / progress.total_stages) * 100) 
    : 0

  return (
    <div className="max-w-2xl mx-auto bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 shadow-sm p-8 animate-fade-in">
      <div className="flex items-center justify-between mb-8 pb-6 border-b border-gray-100 dark:border-gray-800">
        <div>
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">Generating Research Intelligence</h2>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">This may take 2-3 minutes to complete comprehensively.</p>
        </div>
        <div className="text-3xl font-extrabold text-primary-600 dark:text-primary-500">
          {percentComplete}%
        </div>
      </div>
      
      <div className="space-y-6">
        {DEFAULT_STAGES.map((defaultStage, index) => {
          const apiStage = progress.stages.find(s => s.name === defaultStage.name) || {
            name: defaultStage.name,
            status: index < progress.current_stage ? 'completed' : index === progress.current_stage ? 'running' : 'pending',
            message: ''
          }
          
          const Icon = defaultStage.icon
          const isCompleted = apiStage.status === 'completed'
          const isRunning = apiStage.status === 'running'
          const isFailed = apiStage.status === 'failed'
          const isPending = apiStage.status === 'pending'
          
          return (
            <div key={index} className="relative flex items-start gap-4">
              {index < DEFAULT_STAGES.length - 1 && (
                <div 
                  className={`absolute left-5 top-10 bottom-[-24px] w-0.5 ${
                    isCompleted ? 'bg-primary-500 dark:bg-primary-600' : 'bg-gray-200 dark:bg-gray-800'
                  }`} 
                />
              )}
              
              <div 
                className={`relative z-10 flex items-center justify-center w-10 h-10 rounded-full shrink-0 border-2 transition-colors ${
                  isCompleted ? 'bg-primary-500 border-primary-500 text-white' :
                  isRunning ? 'bg-primary-50 border-primary-500 text-primary-600 dark:bg-primary-900/30 dark:border-primary-500 dark:text-primary-400' :
                  isFailed ? 'bg-red-500 border-red-500 text-white' :
                  'bg-white border-gray-200 text-gray-400 dark:bg-gray-900 dark:border-gray-700 dark:text-gray-600'
                }`}
              >
                {isCompleted ? <Check className="w-5 h-5" /> : 
                 isRunning ? <Loader2 className="w-5 h-5 animate-spin" /> : 
                 isFailed ? <X className="w-5 h-5" /> : 
                 <Icon className="w-4 h-4" />}
              </div>
              
              <div className="flex-1 pt-2">
                <div className={`font-medium ${
                  isCompleted || isRunning ? 'text-gray-900 dark:text-white' : 
                  'text-gray-500 dark:text-gray-500'
                }`}>
                  {apiStage.name}
                </div>
                {apiStage.message && isRunning && (
                  <div className="text-sm text-primary-600 dark:text-primary-400 mt-1 animate-pulse">
                    {apiStage.message}
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
