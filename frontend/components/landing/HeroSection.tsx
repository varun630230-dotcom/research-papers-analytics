import React from 'react'
import { ThemeToggle } from '@/components/ui/ThemeToggle'

export function HeroSection() {
  return (
    <div className="relative pt-12 pb-16 px-6 lg:px-8 text-center bg-hero-gradient overflow-hidden">
      <div className="absolute top-6 left-6 font-bold text-xl tracking-tight flex items-center gap-2 text-gradient">
        INNOVATE AI
      </div>
      <div className="absolute top-6 right-6">
        <ThemeToggle />
      </div>
      
      <div className="max-w-4xl mx-auto pt-16">
        <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight text-gray-900 dark:text-white mb-6 animate-slide-up">
          What do you want to <span className="text-gradient">build?</span>
        </h1>
        <p className="text-lg md:text-xl text-gray-600 dark:text-gray-300 mb-8 max-w-2xl mx-auto animate-fade-in opacity-0" style={{ animationDelay: '0.2s', animationFillMode: 'forwards' }}>
          Explore research, technologies, existing solutions, gaps, and opportunities before building your idea.
        </p>
        <p className="text-sm font-medium text-gray-500 dark:text-gray-400 animate-fade-in opacity-0" style={{ animationDelay: '0.4s', animationFillMode: 'forwards' }}>
          Don't just build ideas. Discover what should be built.
        </p>
      </div>
    </div>
  )
}
