const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api";

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

const buildErrorMessage = (data, response) => {
  if (response?.status === 404) return "API endpoint not found.";
  if (response?.status === 401) return "Unauthorized. Please login again.";
  if (response?.status === 403) return "You do not have permission to perform this action.";
  if (response?.status === 500) return "Server error. Please try again.";

  if (!data) return "Request failed";

  if (typeof data === "string") {
    if (data.includes("<!DOCTYPE html>")) {
      return `Request failed with status ${response?.status || ""}`.trim();
    }
    return data;
  }

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
    throw new Error(buildErrorMessage(data, response));
  }

  return data;
}