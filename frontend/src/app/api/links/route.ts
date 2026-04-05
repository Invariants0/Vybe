const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:5000';

export async function GET() {
  const res = await fetch(`${BACKEND_URL}/urls`);
  const data = await res.json();
  return Response.json(data, { status: res.status });
}

export async function POST(request: Request) {
  const body = await request.json();
  const res = await fetch(`${BACKEND_URL}/urls`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  const data = await res.json();
  return Response.json(data, { status: res.status });
}
