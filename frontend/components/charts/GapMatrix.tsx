"use client";

import { Gap, MarketGap } from '@/types';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { Card, CardContent } from '@/components/ui/Card';

interface GapMatrixProps {
  gaps: Gap[];
  marketGaps: MarketGap[];
}

export function GapMatrix({ gaps, marketGaps }: GapMatrixProps) {
  if (!gaps.length && !marketGaps.length) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500 dark:text-gray-400">
        Insufficient data for gap matrix visualization.
      </div>
    );
  }

  // Convert confidence to a 0-100 score for X-axis (Research Maturity)
  const getConfidenceScore = (confidence?: string) => {
    switch (confidence?.toLowerCase()) {
      case 'high': return 90;
      case 'medium': return 60;
      case 'low': return 30;
      default: return 50;
    }
  };

  // Convert gap evidence to a 0-100 score for Y-axis (Market Opportunity)
  const getOpportunityScore = (confidence?: string) => {
    switch (confidence?.toLowerCase()) {
      case 'high': return 90;
      case 'medium': return 60;
      case 'low': return 30;
      default: return 50;
    }
  };

  const data = [
    ...gaps.map((gap, i) => ({
      id: `research-${i}`,
      name: gap.title,
      x: getConfidenceScore(gap.confidence),
      y: getOpportunityScore(gap.validation_status),
      type: 'research',
    })),
    ...marketGaps.map((gap, i) => ({
      id: `market-${i}`,
      name: gap.problem,
      x: getConfidenceScore(gap.confidence),
      y: getOpportunityScore(gap.evidence_type), // Using evidence type for Y axis proxy
      type: 'market',
    }))
  ];

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <Card className="bg-white/90 dark:bg-gray-900/90 border-gray-200 dark:border-gray-800 p-2 shadow-lg backdrop-blur-sm">
          <p className="font-semibold text-sm text-gray-900 dark:text-gray-100 max-w-xs">{data.name}</p>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 uppercase tracking-wider">{data.type} gap</p>
        </Card>
      );
    }
    return null;
  };

  return (
    <div className="h-80 w-full relative">
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none opacity-10">
        <div className="w-full h-full grid grid-cols-2 grid-rows-2">
          <div className="border-r border-b border-gray-400 flex items-center justify-center"><span className="text-sm font-semibold uppercase">Low Priority</span></div>
          <div className="border-b border-gray-400 flex items-center justify-center"><span className="text-sm font-semibold uppercase">Market Opportunity</span></div>
          <div className="border-r border-gray-400 flex items-center justify-center"><span className="text-sm font-semibold uppercase">Research Opportunity</span></div>
          <div className="flex items-center justify-center"><span className="text-sm font-semibold uppercase">High-Potential</span></div>
        </div>
      </div>
      <ResponsiveContainer width="100%" height="100%">
        <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
          <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
          <XAxis type="number" dataKey="x" name="Research Maturity" domain={[0, 100]} label={{ value: 'Research Maturity', position: 'bottom', fill: 'currentColor', opacity: 0.5 }} />
          <YAxis type="number" dataKey="y" name="Market Opportunity" domain={[0, 100]} label={{ value: 'Market Opportunity', angle: -90, position: 'left', fill: 'currentColor', opacity: 0.5 }} />
          <Tooltip content={<CustomTooltip />} />
          <Scatter name="Gaps" data={data}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.type === 'research' ? '#3b82f6' : '#10b981'} opacity={0.8} />
            ))}
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}
