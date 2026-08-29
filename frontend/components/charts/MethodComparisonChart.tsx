"use client";

import { MethodComparison } from '@/types';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

interface MethodComparisonChartProps {
  methods: MethodComparison[];
}

export function MethodComparisonChart({ methods }: MethodComparisonChartProps) {
  if (!methods || methods.length === 0) {
    return null;
  }

  // Try to extract numeric performance values
  const data = methods.map(m => {
    let numValue = null;
    if (m.performance) {
      // Try to find a percentage or decimal
      const match = m.performance.match(/(\d+(\.\d+)?)/);
      if (match) {
        numValue = parseFloat(match[1]);
      }
    }
    return {
      name: m.method.length > 20 ? m.method.substring(0, 20) + '...' : m.method,
      fullName: m.method,
      value: numValue,
      originalStr: m.performance
    };
  });

  const hasNumericData = data.some(d => d.value !== null);

  if (!hasNumericData) {
    return (
      <div className="flex items-center justify-center p-8 bg-gray-50 dark:bg-gray-800/50 rounded-lg text-sm text-gray-500 dark:text-gray-400 text-center border border-dashed border-gray-200 dark:border-gray-700">
        Performance values are not directly comparable across methods.<br/>
        (Non-numeric values detected)
      </div>
    );
  }

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 p-3 shadow-lg rounded-lg max-w-[200px]">
          <p className="font-semibold text-sm text-gray-900 dark:text-gray-100">{data.fullName}</p>
          <p className="text-sm text-blue-600 dark:text-blue-400 mt-1 font-medium">{data.originalStr}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="h-64 w-full mt-4">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          layout="vertical"
          data={data}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={true} opacity={0.1} />
          <XAxis type="number" hide />
          <YAxis dataKey="name" type="category" width={120} tick={{ fontSize: 12, fill: 'currentColor' }} axisLine={false} tickLine={false} />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={24}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={['#3b82f6', '#10b981', '#8b5cf6', '#f59e0b', '#ec4899'][index % 5]} opacity={0.8} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
