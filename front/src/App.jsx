import React, { Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { SearchProvider } from './contexts/SearchContext';
import Home from './pages/Home';
import LanguageSelector from './components/LanguageSelector';
import './App.css';

function App() {
  return (
    <SearchProvider>
      <Suspense fallback="loading">
        <Router>
          <div className="App">
            <header className="App-header" style={{ padding: '1rem', display: 'flex', justifyContent: 'flex-end' }}>
              <LanguageSelector />
            </header>
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
