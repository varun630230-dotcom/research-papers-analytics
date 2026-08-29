import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { ApiClient } from '@/lib/api'
import { AnalyzeRequest } from '@/types'

export function useAnalysis() {
  const router = useRouter()
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const analyzeIdea = async (request: AnalyzeRequest) => {
    setIsAnalyzing(true)
    setError(null)
    try {
      const response = await ApiClient.analyzeIdea(request)
      router.push(`/project/${response.project_id}`)
    } catch (err: any) {
      setError(err.message || 'An error occurred during analysis')
      setIsAnalyzing(false)
    }
  }

  return { analyzeIdea, isAnalyzing, error }
}
