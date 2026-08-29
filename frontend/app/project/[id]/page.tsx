'use client'

import React from 'react'
import { useProject } from '@/hooks/useProject'
import { AnalysisPipeline } from '@/components/pipeline/AnalysisPipeline'
import { Button } from '@/components/ui/Button'
import { AlertCircle, ArrowLeft } from 'lucide-react'
import Link from 'next/link'
import { DashboardLayout } from '@/components/dashboard/DashboardLayout'
import { ThemeProvider } from '@/components/ThemeProvider'

export default function ProjectPage({ params }: { params: { id: string } }) {
  const { project, isLoading, error } = useProject(params.id)

  if (isLoading && !project) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-950 flex items-center justify-center p-6">
        <div className="animate-pulse flex flex-col items-center">
          <div className="w-12 h-12 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin mb-4"></div>
          <p className="text-gray-500 font-medium">Loading project data...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-950 flex flex-col items-center justify-center p-6 text-center">
        <div className="bg-white dark:bg-gray-900 p-8 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-800 max-w-md w-full">
          <div className="w-16 h-16 bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400 rounded-full flex items-center justify-center mx-auto mb-4">
            <AlertCircle className="w-8 h-8" />
          </div>
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">Error Loading Project</h2>
          <p className="text-gray-500 dark:text-gray-400 mb-6">{error}</p>
          <Link href="/">
            <Button className="w-full gap-2">
              <ArrowLeft className="w-4 h-4" /> Go Back Home
            </Button>
          </Link>
        </div>
      </div>
    )
  }

  if (!project) return null

  if (project.status === 'analyzing' || project.status === 'pending') {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-950 pt-16 pb-20 px-6">
        <div className="max-w-7xl mx-auto mb-8">
          <Link href="/">
            <Button variant="ghost" size="sm" className="gap-2 text-gray-500">
              <ArrowLeft className="w-4 h-4" /> Back
            </Button>
          </Link>
        </div>
        <AnalysisPipeline progress={project.progress} />
      </div>
    )
  }

  if (project.status === 'failed') {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-950 flex flex-col items-center justify-center p-6 text-center">
        <div className="bg-white dark:bg-gray-900 p-8 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-800 max-w-md w-full">
          <div className="w-16 h-16 bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400 rounded-full flex items-center justify-center mx-auto mb-4">
            <AlertCircle className="w-8 h-8" />
          </div>
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">Analysis Failed</h2>
          <p className="text-gray-500 dark:text-gray-400 mb-6">
            {project.error_message || 'An unexpected error occurred during analysis.'}
          </p>
          <Link href="/">
            <Button className="w-full gap-2">
              <ArrowLeft className="w-4 h-4" /> Try Again
            </Button>
          </Link>
        </div>
      </div>
    )
  }

  return (
    <ThemeProvider>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
        {project.status === 'partial' && (
          <div className="bg-amber-50 dark:bg-amber-900/20 border-b border-amber-200 dark:border-amber-800/50 px-6 py-3 flex items-center justify-center gap-2 text-amber-800 dark:text-amber-300 text-sm font-medium">
            <AlertCircle className="w-4 h-4" />
            Partial analysis completed. Some data sources were unavailable.
          </div>
        )}
        <DashboardLayout project={project} />
      </div>
    </ThemeProvider>
  )
}
