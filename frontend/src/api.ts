const API = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api";

export async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers);
  if (!(options.body instanceof URLSearchParams)) headers.set("Content-Type", "application/json");
  const token = localStorage.getItem("token");
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const response = await fetch(`${API}${path}`, { ...options, headers });
  if (!response.ok) throw new Error((await response.json()).detail ?? "Request failed");
  return response.status === 204 ? (undefined as T) : response.json();
}

export type User = { id: number; username: string; email: string };
export type Community = { id: number; name: string; description: string; member_count: number };
export type Proposal = { id: number; community_id: number; title: string; description: string; status: string; author_id: number; created_at: string };
