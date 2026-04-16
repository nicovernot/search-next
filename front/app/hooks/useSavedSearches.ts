/**
 * Gère les opérations CRUD sur les recherches sauvegardées d'un utilisateur connecté :
 * chargement depuis l'API, création, suppression.
 * Résultat : expose `searches`, les états de chargement/erreur, et les actions CRUD.
 */
import { useState, useCallback } from "react";
import { api } from "../lib/api";
import type { SavedSearchRecord, SavedSearchData } from "../types";

export function useSavedSearches(token: string | null) {
  const [searches, setSearches] = useState<SavedSearchRecord[]>([]);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  const fetchSearches = useCallback(async () => {
    if (!token) return;
    try {
      const savedSearchesResponse = await api.getSavedSearches(token);
      if (savedSearchesResponse.ok) {
        const data: SavedSearchRecord[] = await savedSearchesResponse.json();
        setSearches(data);
      }
    } catch { /* silently fail */ }
  }, [token]);

  const saveSearch = useCallback(async (name: string, queryData: SavedSearchData) => {
    if (!token || !name.trim()) return;
    setSaving(true);
    setSaveError(null);
    try {
      const saveResponse = await api.createSavedSearch(token, {
        name: name.trim(),
        query_json: queryData,
      });
      if (saveResponse.ok) {
        setSaveSuccess(true);
        setTimeout(() => setSaveSuccess(false), 2000);
        // Rafraîchit la liste après sauvegarde
        const savedSearchesResponse = await api.getSavedSearches(token);
        if (savedSearchesResponse.ok) {
          setSearches(await savedSearchesResponse.json());
        }
        return true;
      } else {
        const apiErrorMessage = await saveResponse.json().then((d: { detail?: string }) => d.detail).catch(() => null);
        setSaveError(apiErrorMessage || `Erreur ${saveResponse.status}`);
        return false;
      }
    } catch {
      setSaveError("Impossible de joindre le serveur");
      return false;
    } finally {
      setSaving(false);
    }
  }, [token]);

  const deleteSearch = useCallback(async (id: number) => {
    if (!token) return;
    try {
      await api.deleteSavedSearch(token, id);
      setSearches((prev) => prev.filter((savedSearch) => savedSearch.id !== id));
    } catch { /* silently fail */ }
  }, [token]);

  return {
    searches,
    saving, saveSuccess, saveError, setSaveError,
    fetchSearches, saveSearch, deleteSearch,
  };
}
