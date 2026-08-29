import React, { useState } from 'react'
import { Button } from '@/components/ui/Button'
import { Sparkles, AlertCircle } from 'lucide-react'

interface IdeaInputProps {
  value: string
  onChange: (val: string) => void
  onSubmit: () => void
  isAnalyzing: boolean
  error: string | null
}

export function IdeaInput({ value, onChange, onSubmit, isAnalyzing, error }: IdeaInputProps) {
  return (
    <div className="w-full max-w-3xl mx-auto animate-slide-up" style={{ animationDelay: '0.3s', animationFillMode: 'backwards' }}>
      <div className="relative rounded-2xl shadow-sm border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 overflow-hidden focus-within:ring-2 focus-within:ring-primary-500 focus-within:border-transparent transition-all">
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder="Describe your idea, problem, project, or technology you want to explore..."
          className="w-full min-h-[160px] p-6 text-lg bg-transparent border-none focus:ring-0 resize-none text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 outline-none"
          disabled={isAnalyzing}
        />
        
        <div className="flex items-center justify-between px-6 py-4 bg-gray-50 dark:bg-gray-800/50 border-t border-gray-100 dark:border-gray-800">
          <span className="text-sm text-gray-500 dark:text-gray-400 font-medium">
            {value.length} characters
          </span>
          <Button 
            size="lg" 
            onClick={onSubmit} 
            disabled={value.trim().length < 10 || isAnalyzing}
            isLoading={isAnalyzing}
            className="gap-2 rounded-xl"
          >
            {!isAnalyzing && <Sparkles className="w-5 h-5" />}
            Analyze Opportunity
          </Button>
        </div>
      </div>
      
      {error && (
        <div className="mt-4 p-4 flex items-start gap-3 bg-red-50 text-red-800 dark:bg-red-900/30 dark:text-red-300 rounded-xl text-sm animate-fade-in">
          <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
          <p>{error}</p>
        </div>
      )}
    </div>
  )
}
