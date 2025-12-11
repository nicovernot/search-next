import React, { Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { SearchProvider } from './contexts/SearchContext';
import Home from './pages/Home';
import './App.css';

function App() {
  return (
    <SearchProvider>
      <Suspense fallback="loading">
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
