import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import './i18n';
import { validateFrontendEnvironment, logEnvironmentInfo } from './utils/envValidation';

// Validation de l'environnement au démarrage
try {
  const envConfig = validateFrontendEnvironment();
  
  // Afficher les informations de configuration en mode debug
  if (envConfig.debug) {
    logEnvironmentInfo();
  }
  
  console.info('Frontend environment validation successful');
} catch (error) {
  console.error('Failed to start application due to environment errors:', error.message);
  // Afficher un message d'erreur à l'utilisateur
  const root = ReactDOM.createRoot(document.getElementById('root'));
  root.render(
    <React.StrictMode>
      <div style={{ padding: '20px', color: 'red', fontFamily: 'sans-serif' }}>
        <h1>Configuration Error</h1>
        <p>Unable to start the application due to environment configuration errors.</p>
        <p>Please contact the administrator.</p>
      </div>
    </React.StrictMode>
  );
  throw error; // Re-lancer l'erreur pour les outils de monitoring
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
