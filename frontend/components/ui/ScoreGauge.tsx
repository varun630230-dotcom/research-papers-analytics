import React, { useEffect, useState } from 'react'
import { cn } from '@/lib/utils'

interface ScoreGaugeProps {
  score: number
  label: string
  className?: string
}

export function ScoreGauge({ score, label, className }: ScoreGaugeProps) {
  const [animatedScore, setAnimatedScore] = useState(0)
  
  useEffect(() => {
    const timer = setTimeout(() => setAnimatedScore(score), 100)
    return () => clearTimeout(timer)
  }, [score])

  const safeScore = Math.min(100, Math.max(0, animatedScore))
  const radius = 36
  const circumference = 2 * Math.PI * radius
  const strokeDashoffset = circumference - (safeScore / 100) * circumference
  
  let colorClass = 'text-green-500'
  if (safeScore < 40) colorClass = 'text-red-500'
  else if (safeScore < 70) colorClass = 'text-amber-500'

  return (
    <div className={cn('flex flex-col items-center justify-center', className)}>
      <div className="relative inline-flex items-center justify-center">
        <svg className="transform -rotate-90 w-24 h-24">
          <circle
            className="text-gray-200 dark:text-gray-800"
            strokeWidth="8"
            stroke="currentColor"
            fill="transparent"
            r={radius}
            cx="48"
            cy="48"
          />
          <circle
            className={cn('transition-all duration-1000 ease-out', colorClass)}
            strokeWidth="8"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            stroke="currentColor"
            fill="transparent"
            r={radius}
            cx="48"
            cy="48"
          />
        </svg>
        <div className="absolute flex flex-col items-center justify-center text-center">
          <span className="text-xl font-bold text-gray-900 dark:text-white">{Math.round(safeScore)}</span>
        </div>
      </div>
      <span className="mt-2 text-sm font-medium text-gray-600 dark:text-gray-400 text-center">{label}</span>
    </div>
  )
}
