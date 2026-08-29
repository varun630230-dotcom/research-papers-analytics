"use client";

import { OpportunityScores } from '@/types';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Tooltip } from 'recharts';

interface OpportunityRadarProps {
  scores: OpportunityScores;
}

export function OpportunityRadar({ scores }: OpportunityRadarProps) {
  const data = [
    { subject: 'Research Gap', A: scores?.research_gap || 0, fullMark: 100 },
    { subject: 'Market Gap', A: scores?.market_gap || 0, fullMark: 100 },
    { subject: 'Tech Feasibility', A: scores?.technology_feasibility || 0, fullMark: 100 },
    { subject: 'Data Availability', A: scores?.data_availability || 0, fullMark: 100 },
    { subject: 'Innovation', A: scores?.innovation_potential || 0, fullMark: 100 },
    { subject: 'Market Potential', A: scores?.market_potential || 0, fullMark: 100 },
    { subject: 'Evidence', A: scores?.evidence_confidence || 0, fullMark: 100 },
  ];

  return (
    <div className="h-80 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart cx="50%" cy="50%" outerRadius="70%" data={data}>
          <PolarGrid strokeOpacity={0.2} />
          <PolarAngleAxis dataKey="subject" tick={{ fill: 'currentColor', fontSize: 12, opacity: 0.8 }} />
          <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: 'currentColor', opacity: 0.5 }} />
          <Radar name="Score" dataKey="A" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.5} />
          <Tooltip 
            contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)', backgroundColor: 'var(--tw-prose-body, rgba(255, 255, 255, 0.9))' }}
            itemStyle={{ color: '#3b82f6', fontWeight: 'bold' }}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
