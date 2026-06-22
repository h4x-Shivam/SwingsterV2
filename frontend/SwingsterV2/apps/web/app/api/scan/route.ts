import { NextRequest } from "next/server";

export const dynamic = "force-dynamic";

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const mode = searchParams.get("mode") || "VCP";

  // Use an environment variable for the Python API URL, fallback to local FastAPI default
  const apiUrl = process.env.NEXT_PUBLIC_PYTHON_API_URL || "http://127.0.0.1:8000";

  try {
    const response = await fetch(`${apiUrl}/scan?mode=${mode}`, {
      method: "GET",
      headers: {
        "Accept": "text/event-stream",
      },
    });

    if (!response.ok) {
      throw new Error(`Python API returned status: ${response.status}`);
    }

    // Proxy the readable stream directly to the client
    return new Response(response.body, {
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
      },
    });
  } catch (error: any) {
    // If the backend is down, we send a fallback SSE message
    const stream = new TransformStream();
    const writer = stream.writable.getWriter();
    const encoder = new TextEncoder();
    writer.write(encoder.encode(`data: ${JSON.stringify(`[SYSTEM_ERROR] Failed to connect to Python backend: ${error.message}`)}\n\n`));
    writer.close();

    return new Response(stream.readable, {
      headers: {
        "Content-Type": "text/event-stream",
      },
    });
  }
}
