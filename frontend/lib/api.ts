import { AnalyzeRequest, AnalyzeResponse, ProjectResult, AnalysisProgress } from '@/types'

const API_URL = process.env.NEXT_PUBLIC_API_URL || ''

export class ApiClient {
  static async analyzeIdea(request: AnalyzeRequest): Promise<AnalyzeResponse> {
    const res = await fetch(`${API_URL}/api/projects/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    })
    if (!res.ok) throw new Error('Failed to start analysis. Please try again.')
    return res.json()
  }

  static async getProject(id: string): Promise<ProjectResult> {
    const res = await fetch(`${API_URL}/api/projects/${id}`)
    if (!res.ok) throw new Error('Failed to fetch project data.')
    return res.json()
  }

  static async getProjectStatus(id: string): Promise<{ status: string; progress: AnalysisProgress }> {
    const res = await fetch(`${API_URL}/api/projects/${id}/status`)
    if (!res.ok) throw new Error('Failed to fetch project status.')
    return res.json()
  }

  static async exportProject(id: string, format: 'markdown' | 'json'): Promise<string> {
    const res = await fetch(`${API_URL}/api/projects/${id}/export`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ format }),
    })
    if (!res.ok) throw new Error('Failed to export project.')
    const data = await res.json()
    return data.content
  }
}

export const api = ApiClient
