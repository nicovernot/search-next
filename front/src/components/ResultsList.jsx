import React from 'react';
import { useSearch } from '../contexts/SearchContext';
import ResultItem from './ResultItem';
import Pagination from './Pagination';
import './ResultsList.css';

function ResultsList() {
  const { results, total, loading, error, query } = useSearch();

  if (loading) {
    return (
      <div className="results-list">
        <div className="loading">Chargement des résultats...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="results-list">
        <div className="no-results">
          Erreur lors de la recherche: {error}
        </div>
      </div>
    );
  }

  if (!query && results.length === 0) {
    return (
      <div className="results-list">
        <div className="no-search">
          Effectuez une recherche pour afficher des résultats
        </div>
      </div>
    );
  }

  if (results.length === 0) {
    return (
      <div className="results-list">
        <div className="no-results">
          Aucun résultat trouvé pour votre recherche
        </div>
      </div>
    );
  }

  return (
    <div className="results-list">
      <div className="results-header">
        <p className="results-count">
          <strong>{total.toLocaleString()}</strong> résultat{total > 1 ? 's' : ''} trouvé{total > 1 ? 's' : ''}
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
