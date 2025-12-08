import React, { createContext, useContext, useState, useCallback } from 'react';
import { search as searchAPI } from '../services/api';

const SearchContext = createContext();

// Mapping entre identifiants de facettes et champs Solr
const FACET_FIELD_MAPPING = {
  'platform': 'platformID',
  'type': 'type',
  'access': 'accessRights_openAireV3',
  'translations': 'autodetect_lang',
  'date': 'anneedatepubli',
  'author': 'contributeurFacetR_auteur'
};

// Mapping inverse pour retrouver l'identifiant depuis le champ Solr
const SOLR_TO_FACET_ID = Object.entries(FACET_FIELD_MAPPING).reduce((acc, [id, field]) => {
  acc[field] = id;
  return acc;
}, {});

export function SearchProvider({ children }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [facets, setFacets] = useState({});
  const [filters, setFilters] = useState({}); // Changed: Object instead of Array
  const [pagination, setPagination] = useState({ from: 0, size: 10 });
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const executeSearch = useCallback(async () => {
    const hasFilters = Object.keys(filters).some(key => filters[key].length > 0);
    if (!query && !hasFilters) {
      setResults([]);
      setTotal(0);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Convert filters from { field: [values] } to [{ identifier, value }]
      const formattedFilters = Object.entries(filters).flatMap(([field, values]) =>
        values.map(value => ({ identifier: field, value: value }))
      );

      const searchRequest = {
        query: { query: query || '*' },
        filters: formattedFilters,
        facets: [
          { identifier: 'platform', type: 'list' },
          { identifier: 'type', type: 'list' },
          { identifier: 'access', type: 'list' },
          { identifier: 'translations', type: 'list' }
          // Note: 'date' et 'author' nécessitent un traitement spécial côté backend
          // (facet.range pour date, vérification d'existence pour author)
        ],
        pagination: {
          from: pagination.from,
          size: pagination.size
        }
      };

      const response = await searchAPI(searchRequest);
      
      setResults(response.response?.docs || []);
      setTotal(response.response?.numFound || 0);
      
      // Transformer les facettes de Solr (tableau plat) en format {facetId: {buckets: [{key, doc_count}]}}
      const rawFacets = response.facet_counts?.facet_fields || {};
      const transformedFacets = {};
      
      Object.entries(rawFacets).forEach(([solrField, values]) => {
        // Trouver l'identifiant de facette correspondant
        const facetId = SOLR_TO_FACET_ID[solrField] || solrField;
        
        // Les facettes Solr sont au format [key1, count1, key2, count2, ...]
        const buckets = [];
        for (let i = 0; i < values.length; i += 2) {
          buckets.push({
            key: values[i],
            doc_count: values[i + 1]
          });
        }
        transformedFacets[facetId] = { buckets };
      });
      
      setFacets(transformedFacets);
    } catch (err) {
      console.error('Search error:', err);
      setError(err.message);
      setResults([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }, [query, filters, pagination]);

  const addFilter = useCallback((field, value) => {
    setFilters(prev => {
      const currentValues = prev[field] || [];
      if (!currentValues.includes(value)) {
        return { ...prev, [field]: [...currentValues, value] };
      }
      return prev;
    });
    setPagination(prev => ({ ...prev, from: 0 }));
  }, []);

  const removeFilter = useCallback((field, value) => {
    setFilters(prev => {
      const currentValues = prev[field] || [];
      const newValues = currentValues.filter(v => v !== value);
      if (newValues.length === 0) {
        const { [field]: _, ...rest } = prev;
        return rest;
      }
      return { ...prev, [field]: newValues };
    });
    setPagination(prev => ({ ...prev, from: 0 }));
  }, []);

  const clearFilters = useCallback(() => {
    setFilters({});
    setPagination(prev => ({ ...prev, from: 0 }));
  }, []);

  const setPage = useCallback((page) => {
    setPagination(prev => ({ ...prev, from: (page - 1) * prev.size }));
  }, []);

  const value = {
    query,
    setQuery,
    results,
    facets,
    filters,
    addFilter,
    removeFilter,
    clearFilters,
    pagination,
    setPage,
    total,
    loading,
    error,
    executeSearch
  };

  return (
    <SearchContext.Provider value={value}>
      {children}
    </SearchContext.Provider>
  );
}

export function useSearch() {
  const context = useContext(SearchContext);
  if (!context) {
    throw new Error('useSearch must be used within a SearchProvider');
  }
  return context;
}
