import React, { useEffect } from 'react';
import { useSearch } from '../contexts/SearchContext';
import './SearchBar.css';

function SearchBar() {
  const { query, setQuery, executeSearch } = useSearch();

  const handleSearch = (e) => {
    e.preventDefault();
    executeSearch();
  };

  const handleInputChange = (e) => {
    setQuery(e.target.value);
  };

  // Recherche automatique quand la query change (avec debounce)
  useEffect(() => {
    if (query.length > 2 || query.length === 0) {
      const timer = setTimeout(() => {
        executeSearch();
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [query, executeSearch]);

  return (
    <form className="search-bar" onSubmit={handleSearch}>
      <div className="search-input-wrapper">
        <input
          type="text"
          name="search"
          className="search-input"
          placeholder="Rechercher dans OpenEdition..."
          value={query}
          onChange={handleInputChange}
          autoComplete="off"
        />
        <button type="submit" className="search-button">
          <svg 
            xmlns="http://www.w3.org/2000/svg" 
            width="20" 
            height="20" 
            viewBox="0 0 24 24" 
            fill="none" 
            stroke="currentColor" 
            strokeWidth="2"
          >
            <circle cx="11" cy="11" r="8"></circle>
            <path d="m21 21-4.35-4.35"></path>
          </svg>
          Rechercher
        </button>
      </div>
    </form>
  );
}

export default SearchBar;
