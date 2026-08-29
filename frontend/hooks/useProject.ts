import { useState, useEffect, useCallback } from 'react'
import { ApiClient } from '@/lib/api'
import { ProjectResult } from '@/types'

export function useProject(id: string) {
  const [project, setProject] = useState<ProjectResult | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchProject = useCallback(async () => {
    try {
      const data = await ApiClient.getProject(id)
      setProject(data)
      setIsLoading(false)
      return data
    } catch (err: any) {
      setError(err.message || 'Failed to fetch project')
      setIsLoading(false)
      return null
    }
  }, [id])

  useEffect(() => {
    let timeoutId: NodeJS.Timeout
    let isMounted = true

    const poll = async () => {
      const data = await fetchProject()
      if (!isMounted) return

      if (data && (data.status === 'analyzing' || data.status === 'pending')) {
        timeoutId = setTimeout(poll, 2000)
      }
    }

    setIsLoading(true)
    poll()

    return () => {
      isMounted = false
      if (timeoutId) clearTimeout(timeoutId)
    }
  }, [fetchProject])

  return { project, isLoading, error, refetch: fetchProject }
}
