import { NextResponse } from 'next/server';

export async function GET(request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return NextResponse.json({ id, message: 'Link details' });
}

export async function PATCH(request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const body = await request.json();
  return NextResponse.json({ id, ...body });
}

export async function DELETE(request: Request, { params }: { params: Promise<{ id: string }> }) {
  await params;
  return NextResponse.json({ success: true });
}
