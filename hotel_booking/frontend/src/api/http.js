const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api";

export class ApiError extends Error {
  constructor(message, status, data = null) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.data = data;
  }
}

export const getAccessToken = () => localStorage.getItem("access");
export const getRefreshToken = () => localStorage.getItem("refresh");

export const setAuthTokens = (data) => {
  if (data?.access) localStorage.setItem("access", data.access);
  if (data?.refresh) localStorage.setItem("refresh", data.refresh);
};

export const clearAuth = () => {
  localStorage.removeItem("access");
  localStorage.removeItem("refresh");
};

const buildErrorMessage = (data) => {
  if (!data) return "Request failed";
  if (typeof data === "string") return data;
  if (data.detail) return data.detail;
  if (data.error) return data.error;
  if (data.message) return data.message;

  const firstValue = Object.values(data)[0];

  if (Array.isArray(firstValue)) return firstValue[0];
  if (typeof firstValue === "string") return firstValue;

  if (typeof firstValue === "object" && firstValue !== null) {
    const nested = Object.values(firstValue)[0];
    if (Array.isArray(nested)) return nested[0];
    if (typeof nested === "string") return nested;
  }

  return "Request failed";
};

export async function apiRequest(endpoint, options = {}) {
  const token = getAccessToken();
  const isFormData = options.body instanceof FormData;

  const headers = {
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(isFormData ? {} : { "Content-Type": "application/json" }),
    ...(options.headers || {}),
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: options.method || "GET",
    headers,
    body: options.body,
  });

  const contentType = response.headers.get("content-type") || "";
  let data = null;

  try {
    if (response.status === 204) {
      data = null;
    } else if (contentType.includes("application/json")) {
      data = await response.json();
    } else {
      const text = await response.text();
      data = text || null;
    }
  } catch {
    data = null;
  }

  if (!response.ok) {
    throw new ApiError(buildErrorMessage(data), response.status, data);
  }

  return data;
}