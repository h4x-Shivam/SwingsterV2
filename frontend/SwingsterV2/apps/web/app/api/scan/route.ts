import { NextRequest } from "next/server";
import { spawn } from "child_process";
import fs from "fs";
import path from "path";

export const dynamic = "force-dynamic";

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const mode = searchParams.get("mode") || "VCP";

  // Determine the root of the SwingsterV2 backend
  // Assuming Next.js runs from frontend/SwingsterV2/apps/web
  const backendRoot = path.resolve(process.cwd(), "../../../../");
  
  // Prioritize the local virtual environment Python executable
  const venvPythonPath = path.join(backendRoot, ".venv", "Scripts", "python.exe");
  const pythonExecutable = fs.existsSync(venvPythonPath) ? venvPythonPath : "python";

  // Create a stream to send Server-Sent Events (SSE) to the frontend
  const stream = new TransformStream();
  const writer = stream.writable.getWriter();
  const encoder = new TextEncoder();

  // Helper to write SSE formatted data
  const send = (msg: string) => {
    writer.write(encoder.encode(`data: ${JSON.stringify(msg)}\n\n`));
  };

  try {
    const child = spawn(pythonExecutable, ["main.py", "--mode", mode], {
      cwd: backendRoot,
      env: {
        ...process.env,
        PYTHONUNBUFFERED: "1", // Force Python to flush stdout immediately
      },
    });

    child.stdout.on("data", (data: Buffer) => {
      const lines = data.toString().split("\n");
      for (const line of lines) {
        if (line.trim()) {
          send(line.trim());
        }
      }
    });

    child.stderr.on("data", (data: Buffer) => {
      const lines = data.toString().split("\n");
      for (const line of lines) {
        if (line.trim()) {
          send(`[WARN] ${line.trim()}`);
        }
      }
    });

    child.on("close", (code) => {
      send(`[SYSTEM] Process exited with code ${code}`);
      writer.close();
    });

    child.on("error", (error) => {
      send(`[SYSTEM_ERROR] Failed to start scan engine: ${error.message}`);
      writer.close();
    });

    return new Response(stream.readable, {
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
      },
    });
  } catch (error: any) {
    send(`[SYSTEM_ERROR] Server Exception: ${error.message}`);
    writer.close();
    return new Response(stream.readable, {
      headers: {
        "Content-Type": "text/event-stream",
      },
    });
  }
}
