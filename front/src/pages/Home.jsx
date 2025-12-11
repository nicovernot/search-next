import React from 'react';
import { useTranslation } from 'react-i18next';
import LanguageSelector from '../components/LanguageSelector';
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
          <div className="header-content" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <h1 className="site-title" style={{ margin: 0 }}>{t('welcome')}</h1>
            <LanguageSelector />
          </div>
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
