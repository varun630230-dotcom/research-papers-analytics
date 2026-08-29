'use client'

import React, { useState } from 'react'
import { HeroSection } from '@/components/landing/HeroSection'
import { IdeaInput } from '@/components/landing/IdeaInput'
import { ExampleCards } from '@/components/landing/ExampleCards'
import { AdvancedConfig, AdvancedConfigData } from '@/components/landing/AdvancedConfig'
import { useAnalysis } from '@/hooks/useAnalysis'

export default function LandingPage() {
  const [idea, setIdea] = useState('')
  const [config, setConfig] = useState<AdvancedConfigData>({
    goal: 'Research Project',
    domain: 'Artificial Intelligence',
    technical_level: 'Intermediate',
    constraints: ''
  })
  
  const { analyzeIdea, isAnalyzing, error } = useAnalysis()

  const handleAnalyze = () => {
    analyzeIdea({
      idea,
      ...config
    })
  }

  return (
    <main className="min-h-screen bg-gray-50 dark:bg-gray-950 pb-20">
      <HeroSection />
      
      <div className="px-6 lg:px-8 max-w-7xl mx-auto -mt-4 relative z-10">
        <IdeaInput 
          value={idea}
          onChange={setIdea}
          onSubmit={handleAnalyze}
          isAnalyzing={isAnalyzing}
          error={error}
        />
        
        <AdvancedConfig 
          config={config}
          onChange={setConfig}
          disabled={isAnalyzing}
        />
        
        <ExampleCards 
          onSelect={setIdea}
          disabled={isAnalyzing}
        />
      </div>
    </main>
  )
}
