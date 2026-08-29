import React from 'react'
import { Badge } from './Badge'
import { getEvidenceColor, getConfidenceColor } from '@/lib/utils'
import { CheckCircle2, Info, AlertTriangle, Lightbulb, ShieldCheck } from 'lucide-react'

interface ConfidenceBadgeProps {
  type?: string
  level?: string
  label?: string
  className?: string
}

export function ConfidenceBadge({ type, level, label, className }: ConfidenceBadgeProps) {
  const displayVal = level || type || 'EVIDENCE'
  const displayUpper = displayVal.toUpperCase()

  let colorClass = getEvidenceColor(displayVal)
  if (level && !type) {
    colorClass = `${getConfidenceColor(level)} border`
  }

  let Icon = Info
  if (displayUpper === 'FACT' || displayUpper === 'EVIDENCE-BACKED' || displayUpper === 'HIGH') {
    Icon = CheckCircle2
  } else if (displayUpper === 'HYPOTHESIS' || displayUpper === 'HYPOTHESIS REQUIRING VALIDATION' || displayUpper === 'LOW') {
    Icon = AlertTriangle
  } else if (displayUpper === 'RECOMMENDATION' || displayUpper === 'POSSIBLE OPPORTUNITY') {
    Icon = Lightbulb
  } else if (displayUpper === 'STRONG INFERENCE' || displayUpper === 'MEDIUM-HIGH' || displayUpper === 'MEDIUM') {
    Icon = ShieldCheck
  }

  return (
    <Badge className={`border gap-1.5 ${colorClass} ${className || ''}`} variant="outline" title={label ? `${label}: ${displayVal}` : displayVal}>
      <Icon className="w-3.5 h-3.5" />
      <span>{label ? `${label}: ${displayVal}` : displayVal}</span>
    </Badge>
  )
}
