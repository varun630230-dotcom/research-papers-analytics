import React from 'react'
import { cn } from '@/lib/utils'

interface ProgressBarProps {
  value: number
  label?: string
  className?: string
  colorClass?: string
}

export function ProgressBar({ value, label, className, colorClass = 'bg-primary-600 dark:bg-primary-500' }: ProgressBarProps) {
  const safeValue = Math.min(100, Math.max(0, value))
  
  return (
    <div className={cn('w-full', className)}>
      {label && (
        <div className="flex justify-between mb-1 text-sm font-medium">
          <span>{label}</span>
          <span>{safeValue}%</span>
        </div>
      )}
      <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-800 overflow-hidden">
        <div 
          className={cn('h-2.5 rounded-full transition-all duration-500 ease-out', colorClass)}
          style={{ width: `${safeValue}%` }}
        ></div>
      </div>
    </div>
  )
}
