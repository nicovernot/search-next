/**
 * Client API centralisé — tous les appels vers le backend passent par ici.
 * - Gestion unifiée de la base URL
 * - Injection automatique du header Authorization quand un token est fourni
 * - Retourne des Response brutes (les appelants gèrent le JSON et les erreurs)
 */

const API_API_BASE_URL_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8003";

function buildJsonAuthHeaders(token?: string | null): HeadersInit {
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

function buildBearerAuthHeaders(token: string): HeadersInit {
  return { Authorization: `Bearer ${token}` };
}

export const api = {
  // --- Search ---

  search(body: object, lang: string): Promise<Response> {
    return fetch(`${API_BASE_URL}/search`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "Accept-Language": lang },
      body: JSON.stringify(body),
    });
  },

  suggest(q: string): Promise<Response> {
    return fetch(`${API_BASE_URL}/suggest?q=${encodeURIComponent(q)}`);
  },

  facetsConfig(): Promise<Response> {
    return fetch(`${API_BASE_URL}/facets/config`);
  },

  // --- Auth ---

  login(email: string, password: string): Promise<Response> {
    return fetch(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      headers: buildJsonAuthHeaders(),
      body: JSON.stringify({ email, password }),
    });
  },

  register(email: string, password: string): Promise<Response> {
    return fetch(`${API_BASE_URL}/auth/register`, {
      method: "POST",
      headers: buildJsonAuthHeaders(),
      body: JSON.stringify({ email, password }),
    });
  },

  // --- Saved searches ---

  getSavedSearches(token: string): Promise<Response> {
    return fetch(`${API_BASE_URL}/saved-searches`, {
      headers: buildBearerAuthHeaders(token),
    });
  },

  createSavedSearch(token: string, body: object): Promise<Response> {
    return fetch(`${API_BASE_URL}/saved-searches`, {
      method: "POST",
      headers: buildJsonAuthHeaders(token),
      body: JSON.stringify(body),
    });
  },

  deleteSavedSearch(token: string, id: number): Promise<Response> {
    return fetch(`${API_BASE_URL}/saved-searches/${id}`, {
      method: "DELETE",
      headers: buildBearerAuthHeaders(token),
    });
  },

  // --- Permissions ---

  permissions(urls: string[]): Promise<Response> {
    return fetch(`${API_BASE_URL}/permissions?urls=${urls.map(encodeURIComponent).join(",")}`);
  },
};
