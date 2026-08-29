"use client";

import { Paper } from '@/types';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface ResearchTimelineProps {
  papers: Paper[];
}

export function ResearchTimeline({ papers }: ResearchTimelineProps) {
  if (papers.length < 2) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500 dark:text-gray-400">
        Insufficient data for timeline visualization.
      </div>
    );
  }

  // Aggregate papers by year
  const yearCounts: Record<string, number> = {};
  papers.forEach(paper => {
    if (paper.year) {
      yearCounts[paper.year] = (yearCounts[paper.year] || 0) + 1;
    }
  });

  const data = Object.entries(yearCounts)
    .map(([year, count]) => ({ year, count }))
    .sort((a, b) => parseInt(a.year) - parseInt(b.year));

  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" opacity={0.2} vertical={false} />
          <XAxis dataKey="year" axisLine={false} tickLine={false} />
          <YAxis allowDecimals={false} axisLine={false} tickLine={false} />
          <Tooltip 
            cursor={{ fill: 'rgba(59, 130, 246, 0.1)' }}
            contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
          />
          <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
