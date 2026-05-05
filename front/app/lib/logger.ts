/**
 * Wrapper de logging frontend.
 * - En dev  : affiche dans la console avec le niveau approprié.
 * - En prod : seuls warn et error sont émis ; debug et info sont silencés.
 *
 * Règles d'usage :
 * - Ne jamais passer de token, email, payload de formulaire ou réponse auth complète.
 * - Préférer un message court + un objet de contexte sans données personnelles.
 */

const isDev = process.env.NODE_ENV !== "production";

function formatMessage(level: string, message: string): string {
  return `[${level.toUpperCase()}] ${message}`;
}

export const logger = {
  debug(message: string, ...args: unknown[]): void {
    if (isDev) console.debug(formatMessage("debug", message), ...args);
  },

  info(message: string, ...args: unknown[]): void {
    if (isDev) console.info(formatMessage("info", message), ...args);
  },

  warn(message: string, ...args: unknown[]): void {
    console.warn(formatMessage("warn", message), ...args);
  },

  error(message: string, ...args: unknown[]): void {
    console.error(formatMessage("error", message), ...args);
  },
};
