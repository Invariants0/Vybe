const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:5000';

export async function GET(request: Request, { params }: { params: Promise<{ code: string }> }) {
  const { code } = await params;

  const res = await fetch(`${BACKEND_URL}/${code}`, { redirect: 'manual' });

  if (res.status >= 300 && res.status < 400) {
    const location = res.headers.get('Location');
    if (location) {
      return Response.redirect(location, res.status);
    }
  }

  return new Response('Link not found', { status: 404 });
}
