import React, { createContext, useContext, useState } from 'react'
import { cn } from '@/lib/utils'

interface TabsContextValue {
  value: string
  onValueChange: (value: string) => void
}

const TabsContext = createContext<TabsContextValue | undefined>(undefined)

export function Tabs({ defaultValue, value, onValueChange, className, children }: {
  defaultValue?: string
  value?: string
  onValueChange?: (value: string) => void
  className?: string
  children: React.ReactNode
}) {
  const [uncontrolledValue, setUncontrolledValue] = useState(defaultValue || '')
  
  const currentValue = value !== undefined ? value : uncontrolledValue
  const handleValueChange = (newValue: string) => {
    if (value === undefined) {
      setUncontrolledValue(newValue)
    }
    onValueChange?.(newValue)
  }

  return (
    <TabsContext.Provider value={{ value: currentValue, onValueChange: handleValueChange }}>
      <div className={cn('w-full', className)}>
        {children}
      </div>
    </TabsContext.Provider>
  )
}

export function TabsList({ className, children }: { className?: string; children: React.ReactNode }) {
  return (
    <div className={cn('flex overflow-x-auto border-b border-gray-200 dark:border-gray-800 scrollbar-thin', className)}>
      {children}
    </div>
  )
}

export function TabsTrigger({ value, className, children, disabled = false }: {
  value: string
  className?: string
  children: React.ReactNode
  disabled?: boolean
}) {
  const context = useContext(TabsContext)
  if (!context) throw new Error('TabsTrigger must be used within a Tabs')
  
  const isActive = context.value === value
  
  return (
    <button
      type="button"
      disabled={disabled}
      onClick={() => context.onValueChange(value)}
      className={cn(
        'inline-flex items-center justify-center whitespace-nowrap px-4 py-3 text-sm font-medium transition-all focus-visible:outline-none disabled:pointer-events-none disabled:opacity-50 border-b-2 -mb-[2px]',
        isActive 
          ? 'border-primary-600 text-primary-600 dark:border-primary-500 dark:text-primary-400' 
          : 'border-transparent text-gray-500 hover:text-gray-900 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-200 dark:hover:border-gray-700',
        className
      )}
    >
      {children}
    </button>
  )
}

export function TabsContent({ value, className, children }: {
  value: string
  className?: string
  children: React.ReactNode
}) {
  const context = useContext(TabsContext)
  if (!context) throw new Error('TabsContent must be used within a Tabs')
  
  if (context.value !== value) return null
  
  return (
    <div className={cn('mt-4 focus-visible:outline-none', className)}>
      {children}
    </div>
  )
}
