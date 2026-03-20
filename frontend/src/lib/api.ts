const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || process.env.BACKEND_URL || "http://localhost:8000";

// Standard API endpoints
export const ENDPOINTS = {
  LOGIN: "/login",
  ME: "/api/users/me",
  JOBS: "/api/crawler/jobs",
  START_CRAWL: "/api/crawler/start",
  LOGOUT: "/api/users/logout",
  GOOGLE_LOGIN: getBackendUrl("/accounts/google/login/"),
  GITHUB_LOGIN: getBackendUrl("/accounts/github/login/"),
};

/**
 * Helper to get the full URL for an endpoint
 * Since Next.js rewrites are configured in next.config.ts,
 * we can use relative paths for client-side fetches.
 * For server-side or absolute redirects, we use the backend URL.
 */
export function getBackendUrl(path: string): string {
  if (path.startsWith("http")) return path;
  return `${BACKEND_URL}${path.startsWith("/") ? "" : "/"}${path}`;
}

/**
 * Helper to get a cookie value by name
 */
function getCookie(name: string): string | null {
  if (typeof document === "undefined") return null;
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop()?.split(";").shift() || null;
  return null;
}

/**
 * Standard fetch wrapper with error handling and JSON parsing
 */
export async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...((options.headers as Record<string, string>) || {}),
  };

  // Add CSRF token for non-safe methods (POST, PUT, DELETE, etc.)
  const method = options.method?.toUpperCase() || "GET";
  if (method !== "GET" && method !== "HEAD") {
    const csrfToken = getCookie("csrftoken");
    if (csrfToken) {
      headers["X-CSRFToken"] = csrfToken;
    }
  }

  const res = await fetch(endpoint, {
    ...options,
    headers,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `API request failed with status ${res.status}`);
  }

  return res.json() as Promise<T>;
}
