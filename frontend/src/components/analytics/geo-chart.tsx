"use client";

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface GeoChartProps {
  data: Array<{ name: string; value: number }>;
}

export function GeoChart({ data }: GeoChartProps) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={data} layout="vertical" margin={{top: 0, right: 0, left: 0, bottom: 0}}>
        <CartesianGrid strokeDasharray="3 3" stroke="#d4d4d4" horizontal={false} />
        <XAxis type="number" hide />
        <YAxis dataKey="name" type="category" stroke="#333333" tick={{fontFamily: 'var(--font-inter)', fontWeight: 'bold'}} width={40} />
        <Tooltip contentStyle={{backgroundColor: '#f7f9fa', border: '2px solid #333333', boxShadow: '4px 4px 0px 0px #333333', fontWeight: 'bold'}} />
        <Bar dataKey="value" fill="#ffc0cb" stroke="#333333" strokeWidth={2} />
      </BarChart>
    </ResponsiveContainer>
  );
}
