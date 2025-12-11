import React from 'react';
import { useTranslation } from 'react-i18next';
import { useSearch } from '../contexts/SearchContext';
import FacetGroup from './FacetGroup';
import './Facets.css';

function Facets() {
  const { t } = useTranslation();
  const { facets, filters, addFilter, removeFilter, clearFilters } = useSearch();

  const handleFilterChange = (field, value, checked) => {
    if (checked) {
      addFilter(field, value);
    } else {
      removeFilter(field, value);
    }
  };

  const handleClearAll = () => {
    clearFilters();
  };

  // Convertir filters object en array pour l'affichage
  const activeFiltersArray = Object.entries(filters).flatMap(([field, values]) =>
    values.map(value => ({ identifier: field, value }))
  );
  const hasActiveFilters = activeFiltersArray.length > 0;

  // Définir les facettes à afficher
  const facetConfigs = [
    { key: 'platform', label: t('platform'), field: 'platform' },
    { key: 'type', label: t('documentType'), field: 'type' },
    { key: 'access', label: t('access'), field: 'access' },
    { key: 'translations', label: t('languageFilter'), field: 'translations' }
    // TODO: Ajouter 'date' (année) et 'author' (auteur) quand le backend les supportera
  ];

  return (
    <div className="facets">
      <div className="facets-header">
        <h3>{t('filters')}</h3>
        {hasActiveFilters && (
          <button
            className="clear-filters-button"
            onClick={handleClearAll}
          >
            {t('resetFilters')}
          </button>
        )}
      </div>

      {hasActiveFilters && (
        <div className="active-filters">
          {activeFiltersArray.map((filter, index) => (
            <div key={index} className="active-filter-tag">
              <span>{filter.identifier}: {filter.value}</span>
              <button
                onClick={() => handleFilterChange(filter.identifier, filter.value, false)}
                className="remove-filter"
              >
                ×
              </button>
            </div>
          ))}
        </div>
      )}

      <div className="facets-groups">
        {facetConfigs.map((config) => {
          const facetData = facets[config.key];
          if (!facetData || !facetData.buckets || facetData.buckets.length === 0) {
            return null;
          }

          return (
            <FacetGroup
              key={config.key}
              label={config.label}
              field={config.field}
              buckets={facetData.buckets}
              activeFilters={activeFiltersArray}
              onFilterChange={handleFilterChange}
            />
          );
        })}
      </div>
    </div>
  );
}

export default Facets;

