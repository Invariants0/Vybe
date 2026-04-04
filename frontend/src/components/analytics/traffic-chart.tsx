'use client';

import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

interface TrafficChartProps {
  data: Array<{ name: string; clicks: number }>;
}

export function TrafficChart({ data }: TrafficChartProps) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#d4d4d4" />
        <XAxis
          dataKey="name"
          stroke="#333333"
          tick={{ fontFamily: 'var(--font-inter)', fontWeight: 'bold' }}
        />
        <YAxis stroke="#333333" tick={{ fontFamily: 'var(--font-inter)', fontWeight: 'bold' }} />
        <Tooltip
          contentStyle={{
            backgroundColor: '#f7f9fa',
            border: '2px solid #333333',
            boxShadow: '4px 4px 0px 0px #333333',
            fontWeight: 'bold',
          }}
        />
        <Line
          type="step"
          dataKey="clicks"
          stroke="#333333"
          strokeWidth={4}
          dot={{ r: 6, fill: '#87ceeb', stroke: '#333333', strokeWidth: 2 }}
          activeDot={{ r: 8 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
