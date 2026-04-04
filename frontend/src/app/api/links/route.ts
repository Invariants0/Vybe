import { linkSchema } from '@/features/links/schema';
import { NextResponse } from 'next/server';

// Mock data - replace with actual database
const mockLinks = [
  {
    id: '1',
    shortCode: 'launch',
    originalUrl: 'https://example.com/campaign-2026',
    title: 'Launch Campaign',
    clicks: 45200,
    status: 'active' as const,
    createdAt: new Date('2026-03-01'),
  },
  {
    id: '2',
    shortCode: 'docs',
    originalUrl: 'https://docs.example.com/v2',
    title: 'Documentation',
    clicks: 12800,
    status: 'active' as const,
    createdAt: new Date('2026-03-15'),
  },
];

export async function GET() {
  try {
    return NextResponse.json(mockLinks);
  } catch (error) {
    return NextResponse.json({ error: 'Failed to fetch links' }, { status: 500 });
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const validated = linkSchema.parse(body);

    // Mock creation - replace with actual database insert
    const newLink = {
      ...validated,
      id: Math.random().toString(36).substring(7),
      createdAt: new Date(),
    };

    return NextResponse.json(newLink, { status: 201 });
  } catch (error) {
    return NextResponse.json({ error: 'Invalid request' }, { status: 400 });
  }
}
