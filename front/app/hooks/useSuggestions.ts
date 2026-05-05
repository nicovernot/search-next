/**
 * Gère l'autocomplétion : appelle /suggest dès que la requête atteint 2 caractères.
 * Résultat : expose `suggestions` (liste de termes), `fetchSuggestions` (déclencheur), `loadingSuggestions`.
 */
import { useState, useCallback } from "react";
import { api } from "../lib/api";
import { logger } from "../lib/logger";

export function useSuggestions() {
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [loadingSuggestions, setLoadingSuggestions] = useState(false);

  const fetchSuggestions = useCallback(async (query: string) => {
    if (!query || query.length < 2) {
      setSuggestions([]);
      return;
    }
    setLoadingSuggestions(true);
    try {
      const res = await api.suggest(query);
      if (!res.ok) throw new Error("Failed to fetch suggestions");
      const data = await res.json();
      setSuggestions(data.suggestions || []);
    } catch (err) {
      logger.error("Suggestions fetch failed");
      setSuggestions([]);
    } finally {
      setLoadingSuggestions(false);
    }
  }, []);

  return { suggestions, fetchSuggestions, loadingSuggestions };
}
