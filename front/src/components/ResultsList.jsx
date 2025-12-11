import React from 'react';
import { useTranslation } from 'react-i18next';
import { useSearch } from '../contexts/SearchContext';
import ResultItem from './ResultItem';
import Pagination from './Pagination';
import './ResultsList.css';

function ResultsList() {
  const { t } = useTranslation();
  const { results, total, loading, error, query } = useSearch();

  if (loading) {
    return (
      <div className="results-list">
        <div className="loading">{t('loading')}</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="results-list">
        <div className="no-results">
          {t('searchError', { error })}
        </div>
      </div>
    );
  }

  if (!query && results.length === 0) {
    return (
      <div className="results-list">
        <div className="no-search">
          {t('noSearch')}
        </div>
      </div>
    );
  }

  if (results.length === 0) {
    return (
      <div className="results-list">
        <div className="no-results">
          {t('noResults')}
        </div>
      </div>
    );
  }

  return (
    <div className="results-list">
      <div className="results-header">
        <p className="results-count">
          <strong>{total.toLocaleString()}</strong> {t('resultsCount', { count: total })}
        </p>
      </div>

      <div className="results-items">
        {results.map((doc, index) => (
          <ResultItem key={doc.url || index} doc={doc} />
        ))}
      </div>

      {total > 10 && <Pagination total={total} />}
    </div>
  );
}

export default ResultsList;

