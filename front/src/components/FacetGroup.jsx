import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import './FacetGroup.css';

function FacetGroup({ label, field, buckets, activeFilters, onFilterChange }) {
  const { t } = useTranslation();
  const [expanded, setExpanded] = useState(true);
  const [showAll, setShowAll] = useState(false);

  const maxVisible = 5;
  const visibleBuckets = showAll ? buckets : buckets.slice(0, maxVisible);
  const hasMore = buckets.length > maxVisible;

  const isChecked = (value) => {
    return activeFilters.some(
      (filter) => filter.identifier === field && filter.value === value
    );
  };

  return (
    <div className="facet-group">
      <button
        className="facet-group-header"
        onClick={() => setExpanded(!expanded)}
      >
        <h4>{label}</h4>
        <span className={`facet-toggle ${expanded ? 'expanded' : ''}`}>
          {expanded ? '−' : '+'}
        </span>
      </button>

      {expanded && (
        <div className="facet-group-content">
          <ul className="facet-list">
            {visibleBuckets.map((bucket) => (
              <li key={bucket.key} className="facet-item">
                <label className="facet-label">
                  <input
                    type="checkbox"
                    checked={isChecked(bucket.key)}
                    onChange={(e) =>
                      onFilterChange(field, bucket.key, e.target.checked)
                    }
                    className="facet-checkbox"
                  />
                  <span className="facet-name">{bucket.key}</span>
                  <span className="facet-count">
                    ({bucket.doc_count.toLocaleString()})
                  </span>
                </label>
              </li>
            ))}
          </ul>

          {hasMore && (
            <button
              className="show-more-button"
              onClick={() => setShowAll(!showAll)}
            >
              {showAll ? t('showLess') : t('showMore', { count: buckets.length - maxVisible })}
            </button>
          )}
        </div>
      )}
    </div>
  );
}

export default FacetGroup;

