const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:5000';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const code = searchParams.get('code');

  const endpoint = code ? `${BACKEND_URL}/events/${code}/analytics` : `${BACKEND_URL}/events`;
  const res = await fetch(endpoint);
  const data = await res.json();
  return Response.json(data, { status: res.status });
}
