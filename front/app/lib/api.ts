/**
 * Client API centralisé — tous les appels vers le backend passent par ici.
 * - Gestion unifiée de la base URL
 * - Injection automatique du header Authorization quand un token est fourni
 * - Retourne des Response brutes (les appelants gèrent le JSON et les erreurs)
 */

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8003";

function jsonHeaders(token?: string | null): HeadersInit {
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

function bearerHeaders(token: string): HeadersInit {
  return { Authorization: `Bearer ${token}` };
}

export const api = {
  // --- Search ---

  search(body: object, lang: string): Promise<Response> {
    return fetch(`${BASE}/search`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "Accept-Language": lang },
      body: JSON.stringify(body),
    });
  },

  suggest(q: string): Promise<Response> {
    return fetch(`${BASE}/suggest?q=${encodeURIComponent(q)}`);
  },

  facetsConfig(): Promise<Response> {
    return fetch(`${BASE}/facets/config`);
  },

  // --- Auth ---

  login(email: string, password: string): Promise<Response> {
    return fetch(`${BASE}/auth/login`, {
      method: "POST",
      headers: jsonHeaders(),
      body: JSON.stringify({ email, password }),
    });
  },

  register(email: string, password: string): Promise<Response> {
    return fetch(`${BASE}/auth/register`, {
      method: "POST",
      headers: jsonHeaders(),
      body: JSON.stringify({ email, password }),
    });
  },

  // --- Saved searches ---

  getSavedSearches(token: string): Promise<Response> {
    return fetch(`${BASE}/saved-searches`, {
      headers: bearerHeaders(token),
    });
  },

  createSavedSearch(token: string, body: object): Promise<Response> {
    return fetch(`${BASE}/saved-searches`, {
      method: "POST",
      headers: jsonHeaders(token),
      body: JSON.stringify(body),
    });
  },

  deleteSavedSearch(token: string, id: number): Promise<Response> {
    return fetch(`${BASE}/saved-searches/${id}`, {
      method: "DELETE",
      headers: bearerHeaders(token),
    });
  },

  // --- Permissions ---

  permissions(urls: string[]): Promise<Response> {
    return fetch(`${BASE}/permissions?urls=${urls.map(encodeURIComponent).join(",")}`);
  },
};
