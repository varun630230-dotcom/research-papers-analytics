import React from 'react'
import { cn } from '@/lib/utils'

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'secondary' | 'success' | 'warning' | 'danger' | 'info' | 'outline'
  size?: 'sm' | 'md'
}

export function Badge({ className, variant = 'default', size = 'sm', children, ...props }: BadgeProps) {
  return (
    <div
      className={cn(
        'inline-flex items-center rounded-full font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 border',
        {
          'bg-gray-100 text-gray-900 border-transparent dark:bg-gray-800 dark:text-gray-100': variant === 'default',
          'bg-gray-200 text-gray-800 border-transparent dark:bg-gray-700 dark:text-gray-200': variant === 'secondary',
          'bg-green-100 text-green-800 border-transparent dark:bg-green-900/30 dark:text-green-300': variant === 'success',
          'bg-amber-100 text-amber-800 border-transparent dark:bg-amber-900/30 dark:text-amber-300': variant === 'warning',
          'bg-red-100 text-red-800 border-transparent dark:bg-red-900/30 dark:text-red-300': variant === 'danger',
          'bg-blue-100 text-blue-800 border-transparent dark:bg-blue-900/30 dark:text-blue-300': variant === 'info',
          'text-gray-950 dark:text-gray-50 border-gray-200 dark:border-gray-800': variant === 'outline',
          'px-2.5 py-0.5 text-xs': size === 'sm',
          'px-3 py-1 text-sm': size === 'md',
        },
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}
