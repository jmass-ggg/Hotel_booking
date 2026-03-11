import { apiRequest, clearAuth, setAuthTokens } from "./http";

export async function loginUser(payload) {
  clearAuth();

  const data = await apiRequest("/auth/login/", {
    method: "POST",
    body: JSON.stringify(payload),
  });

  setAuthTokens(data);
  return data;
}

export function logoutUser() {
  clearAuth();
}

export async function getMe() {
  return apiRequest("/auth/me/", {
    method: "GET",
  });
}