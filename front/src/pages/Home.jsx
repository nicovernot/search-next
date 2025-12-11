import React from 'react';
import { useTranslation } from 'react-i18next';
import SearchBar from '../components/SearchBar';
import ResultsList from '../components/ResultsList';
import Facets from '../components/Facets';
import './Home.css';

function Home() {
  const { t } = useTranslation();

  return (
    <div className="home-page">
      <header className="header">
        <div className="container">
          <h1 className="site-title">{t('welcome')}</h1>
          <SearchBar />
        </div>
      </header>

      <main className="main-content container">
        <aside className="sidebar">
          <Facets />
        </aside>

        <div className="results-area">
          <ResultsList />
        </div>
      </main>
    </div>
  );
}

export default Home;
