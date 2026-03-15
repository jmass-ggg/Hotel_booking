import { apiRequest, clearAuth, setAuthTokens } from "./http";

let meCache = null;
let mePromise = null;

export async function loginUser(payload) {
  clearMeCache();
  clearAuth();

  const data = await apiRequest("/auth/login/", {
    method: "POST",
    body: JSON.stringify(payload),
  });

  setAuthTokens(data);
  return data;
}

export function logoutUser() {
  clearMeCache();
  clearAuth();
}

export function clearMeCache() {
  meCache = null;
  mePromise = null;
  localStorage.removeItem("me");
}

export async function getMe(options = {}) {
  const { forceRefresh = false } = options;

  if (!forceRefresh) {
    if (meCache) {
      return meCache;
    }

    const saved = localStorage.getItem("me");
    if (saved) {
      try {
        meCache = JSON.parse(saved);
        return meCache;
      } catch {
        localStorage.removeItem("me");
      }
    }

    if (mePromise) {
      return mePromise;
    }
  }

  mePromise = apiRequest("/auth/me/", {
    method: "GET",
  })
    .then((data) => {
      meCache = data;
      localStorage.setItem("me", JSON.stringify(data));
      return data;
    })
    .catch((error) => {
      meCache = null;
      localStorage.removeItem("me");
      throw error;
    })
    .finally(() => {
      mePromise = null;
    });

  return mePromise;
}