import { NextResponse } from "next/server";

const API = process.env.API_BASE_URL || "http://localhost:8000";

export async function GET() {
  const res = await fetch(`${API}/calendar/slots?days=7`, { cache: "no-store" });
  const data = await res.json();
  return NextResponse.json(data, { status: res.status });
}
