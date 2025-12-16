/**
 * Validation des variables d'environnement pour le frontend React
 * À appeler au démarrage de l'application (dans index.jsx)
 */

/**
 * Liste des variables d'environnement requises pour le frontend
 * @typedef {Object} RequiredEnvVars
 * @property {string} REACT_APP_API_URL - URL de l'API backend
 * @property {string} [REACT_APP_DEBUG] - Mode debug (optionnel)
 * @property {string} [REACT_APP_MOCK_API] - Utilisation de l'API mock (optionnel)
 * @property {string} NODE_ENV - Environnement (development, production, etc.)
 */

/**
 * Valide les variables d'environnement du frontend
 * @throws {Error} Si une variable requise est manquante ou invalide
 */
export function validateFrontendEnvironment() {
  const errors = [];
  const warnings = [];

  // Variables requises
  const requiredVars = {
    REACT_APP_API_URL: {
      validate: (value) => {
        try {
          new URL(value);
          return true;
        } catch (e) {
          return false;
        }
      },
      message: 'REACT_APP_API_URL must be a valid URL'
    }
  };

  // Variables optionnelles avec validation
  const optionalVars = {
    REACT_APP_DEBUG: {
      validate: (value) => ['true', 'false', '1', '0'].includes(value?.toLowerCase()),
      message: 'REACT_APP_DEBUG must be a boolean value (true/false)'
    },
    REACT_APP_MOCK_API: {
      validate: (value) => ['true', 'false', '1', '0'].includes(value?.toLowerCase()),
      message: 'REACT_APP_MOCK_API must be a boolean value (true/false)'
    }
  };

  // Vérifier les variables requises
  Object.entries(requiredVars).forEach(([name, { validate, message }]) => {
    const value = process.env[name];
    if (!value) {
      errors.push(`Missing required environment variable: ${name}`);
    } else if (!validate(value)) {
      errors.push(`${message} (current: ${value})`);
    }
  });

  // Vérifier les variables optionnelles
  Object.entries(optionalVars).forEach(([name, { validate, message }]) => {
    const value = process.env[name];
    if (value && !validate(value)) {
      warnings.push(`${message} (current: ${value})`);
    }
  });

  // Validation spécifique à l'environnement
  if (process.env.NODE_ENV === 'production') {
    // En production, certaines variables ne devraient pas être activées
    if (process.env.REACT_APP_DEBUG === 'true') {
      warnings.push('REACT_APP_DEBUG should be false in production');
    }
    if (process.env.REACT_APP_MOCK_API === 'true') {
      warnings.push('REACT_APP_MOCK_API should be false in production');
    }
  }

  // Afficher les avertissements
  if (warnings.length > 0) {
    console.warn('Environment variable warnings:');
    warnings.forEach(warning => console.warn(`- ${warning}`));
  }

  // Lancer une erreur si des problèmes critiques
  if (errors.length > 0) {
    console.error('Environment validation errors:');
    errors.forEach(error => console.error(`- ${error}`));
    throw new Error('Invalid environment configuration');
  }

  // Retourner la configuration validée
  return {
    apiUrl: process.env.REACT_APP_API_URL,
    debug: process.env.REACT_APP_DEBUG === 'true',
    mockApi: process.env.REACT_APP_MOCK_API === 'true',
    nodeEnv: process.env.NODE_ENV
  };
}

/**
 * Affiche les informations de configuration (pour le debug)
 */
export function logEnvironmentInfo() {
  console.info('Frontend Environment Configuration:');
  console.info(`- NODE_ENV: ${process.env.NODE_ENV}`);
  console.info(`- REACT_APP_API_URL: ${process.env.REACT_APP_API_URL}`);
  console.info(`- REACT_APP_DEBUG: ${process.env.REACT_APP_DEBUG}`);
  console.info(`- REACT_APP_MOCK_API: ${process.env.REACT_APP_MOCK_API}`);
}