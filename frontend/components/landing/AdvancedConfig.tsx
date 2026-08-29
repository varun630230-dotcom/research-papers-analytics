import React, { useState } from 'react'
import { ChevronDown, ChevronUp, Settings } from 'lucide-react'

export interface AdvancedConfigData {
  goal: string
  domain: string
  technical_level: string
  constraints: string
}

interface AdvancedConfigProps {
  config: AdvancedConfigData
  onChange: (config: AdvancedConfigData) => void
  disabled?: boolean
}

export function AdvancedConfig({ config, onChange, disabled }: AdvancedConfigProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  const handleChange = (field: keyof AdvancedConfigData, value: string) => {
    onChange({ ...config, [field]: value })
  }

  const goals = ['Final Year Project', 'Research Project', 'Startup Idea', 'Product Development', 'Technology Exploration']
  const domains = ['Artificial Intelligence', 'Healthcare', 'Agriculture', 'Education', 'Cybersecurity', 'Finance', 'Environment', 'Computer Vision', 'NLP', 'Robotics', 'Other']
  const levels = ['Beginner', 'Intermediate', 'Advanced']

  return (
    <div className="w-full max-w-3xl mx-auto mt-6 animate-fade-in opacity-0" style={{ animationDelay: '0.4s', animationFillMode: 'forwards' }}>
      <button
        type="button"
        onClick={() => setIsExpanded(!isExpanded)}
        disabled={disabled}
        className="flex items-center gap-2 text-sm font-medium text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-200 mx-auto transition-colors disabled:opacity-50"
      >
        <Settings className="w-4 h-4" />
        Advanced Options
        {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
      </button>

      {isExpanded && (
        <div className="mt-4 p-6 bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 shadow-sm grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Goal</label>
            <select
              value={config.goal}
              onChange={(e) => handleChange('goal', e.target.value)}
              disabled={disabled}
              className="w-full p-2.5 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 outline-none text-gray-900 dark:text-gray-100"
            >
              {goals.map(g => <option key={g} value={g}>{g}</option>)}
            </select>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Domain</label>
            <select
              value={config.domain}
              onChange={(e) => handleChange('domain', e.target.value)}
              disabled={disabled}
              className="w-full p-2.5 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 outline-none text-gray-900 dark:text-gray-100"
            >
              {domains.map(d => <option key={d} value={d}>{d}</option>)}
            </select>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Technical Level</label>
            <div className="flex gap-4">
              {levels.map(l => (
                <label key={l} className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    name="techLevel"
                    value={l}
                    checked={config.technical_level === l}
                    onChange={(e) => handleChange('technical_level', e.target.value)}
                    disabled={disabled}
                    className="text-primary-600 focus:ring-primary-500"
                  />
                  <span className="text-sm text-gray-600 dark:text-gray-400">{l}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="space-y-2 md:col-span-2">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Constraints</label>
            <input
              type="text"
              value={config.constraints}
              onChange={(e) => handleChange('constraints', e.target.value)}
              disabled={disabled}
              placeholder="e.g., must run on mobile, no API keys, under 6 months..."
              className="w-full p-2.5 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 outline-none text-gray-900 dark:text-gray-100 placeholder-gray-400"
            />
          </div>
        </div>
      )}
    </div>
  )
}
