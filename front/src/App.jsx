import React, { Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { SearchProvider } from './contexts/SearchContext';
import Home from './pages/Home';
import './App.css';

function LoadingFallback() {
  const { t } = useTranslation();
  return <div>{t('loading')}</div>;
}

function App() {
  return (
    <SearchProvider>
      <Suspense fallback={<LoadingFallback />}>
        <Router>
          <div className="App">
            <Routes>
              <Route path="/" element={<Home />} />
            </Routes>
          </div>
        </Router>
      </Suspense>
    </SearchProvider>
  );
}

export default App;

