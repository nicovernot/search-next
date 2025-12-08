/**
 * Configuration de Searchkit pour l'application
 */

import Searchkit from '@searchkit/client';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * Configuration du client Searchkit
 * Searchkit va communiquer avec notre API FastAPI
 */
export const searchkitClient = new Searchkit({
  connection: {
    host: API_BASE_URL,
    // Utilise l'endpoint de recherche POST par défaut
    apiKey: process.env.REACT_APP_SEARCHKIT_API_KEY || '',
  },
  search_settings: {
    // Configuration de la recherche par défaut
    search_fields: ['title', 'description', 'content', 'authors'],
    result_fields: ['title', 'description', 'url', 'platform', 'type', 'authors', 'year'],
    highlight_fields: ['title', 'description'],
    snippet_fields: ['description:300'],
    
    // Facettes disponibles
    facets: [
      {
        field: 'platform',
        type: 'RefinementSelectFacet',
        label: 'Plateforme',
        identifier: 'platform',
        display: 'ListFacet',
      },
      {
        field: 'type',
        type: 'RefinementSelectFacet',
        label: 'Type de document',
        identifier: 'type',
        display: 'ListFacet',
      },
      {
        field: 'language',
        type: 'RefinementSelectFacet',
        label: 'Langue',
        identifier: 'language',
        display: 'ListFacet',
      },
      {
        field: 'year',
        type: 'RefinementSelectFacet',
        label: 'Année de publication',
        identifier: 'year',
        display: 'ListFacet',
      },
    ],
  },
});

/**
 * Transforme les paramètres Searchkit en format compatible avec notre API
 * @param {Object} searchkitParams - Paramètres générés par Searchkit
 * @returns {Object} - Requête au format SearchRequest de l'API
 */
export function transformToSearchRequest(searchkitParams) {
  const filters = (searchkitParams.filters || []).map(filter => ({
    identifier: filter.identifier,
    value: filter.value,
  }));

  const facets = (searchkitParams.facets || []).map(facet => ({
    identifier: facet.identifier,
    type: 'list',
  }));

  return {
    query: {
      query: searchkitParams.query || '',
    },
    filters,
    facets,
    pagination: {
      from_: searchkitParams.from || 0,
      size: searchkitParams.size || 10,
    },
  };
}

/**
 * Transforme la réponse de l'API en format compatible avec Searchkit
 * @param {Object} apiResponse - Réponse de l'API FastAPI
 * @returns {Object} - Résultats au format Searchkit
 */
export function transformFromSearchResponse(apiResponse) {
  return {
    hits: {
      hits: apiResponse.hits || [],
      total: {
        value: apiResponse.total || 0,
      },
    },
    aggregations: apiResponse.aggregations || {},
  };
}

export default searchkitClient;
