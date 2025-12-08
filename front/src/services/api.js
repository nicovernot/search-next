/**
 * Service API pour communiquer avec le backend FastAPI
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * Effectue une recherche via l'API FastAPI
 * @param {Object} searchRequest - Requête de recherche au format SearchRequest
 * @returns {Promise<Object>} - Résultats de la recherche
 */
export async function search(searchRequest) {
  const response = await fetch(`${API_BASE_URL}/search`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(searchRequest),
  });

  if (!response.ok) {
    throw new Error(`Search failed: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Effectue une recherche via GET (avec paramètres URL)
 * @param {Object} params - Paramètres de recherche
 * @returns {Promise<Object>} - Résultats de la recherche
 */
export async function searchGet(params) {
  const queryParams = new URLSearchParams();
  
  if (params.q) queryParams.append('q', params.q);
  if (params.page) queryParams.append('page', params.page);
  if (params.size) queryParams.append('size', params.size);
  
  if (params.filters && Array.isArray(params.filters)) {
    params.filters.forEach(filter => {
      queryParams.append('filters', filter);
    });
  }
  
  if (params.facets && Array.isArray(params.facets)) {
    params.facets.forEach(facet => {
      queryParams.append('facets', facet);
    });
  }

  const response = await fetch(`${API_BASE_URL}/search?${queryParams.toString()}`);

  if (!response.ok) {
    throw new Error(`Search failed: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Obtient des suggestions d'autocomplétion
 * @param {string} query - Terme de recherche partiel
 * @returns {Promise<Object>} - Suggestions
 */
export async function suggest(query) {
  const response = await fetch(
    `${API_BASE_URL}/suggest?q=${encodeURIComponent(query)}`
  );

  if (!response.ok) {
    throw new Error(`Suggest failed: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Vérifie les permissions d'accès aux documents
 * @param {string[]} urls - Liste d'URLs de documents
 * @param {string} ip - Adresse IP (optionnel)
 * @returns {Promise<Object>} - Informations de permissions
 */
export async function getPermissions(urls, ip = null) {
  const queryParams = new URLSearchParams({
    urls: urls.join(','),
  });
  
  if (ip) {
    queryParams.append('ip', ip);
  }

  const response = await fetch(`${API_BASE_URL}/permissions?${queryParams.toString()}`);

  if (!response.ok) {
    throw new Error(`Permissions check failed: ${response.statusText}`);
  }

  return response.json();
}

export default {
  search,
  searchGet,
  suggest,
  getPermissions,
};
