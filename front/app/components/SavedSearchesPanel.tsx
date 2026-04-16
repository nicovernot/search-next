"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { createPortal } from "react-dom";
import { useTranslations } from "next-intl";
import { useAuth } from "../context/AuthContext";
import { useSearch } from "../context/SearchContext";
import { Bookmark, Trash2, ChevronDown, Plus, Check } from "lucide-react";
import { api } from "../lib/api";
import type { SavedSearchRecord } from "../types";

export default function SavedSearchesPanel() {
  const t = useTranslations();
  const { token } = useAuth();
  const { query, filters, logicalQuery, searchMode, loadSearch } = useSearch();

  const [open, setOpen] = useState(false);
  const [searches, setSearches] = useState<SavedSearchRecord[]>([]);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [newName, setNewName] = useState("");
  const [showSaveForm, setShowSaveForm] = useState(false);
  const [dropdownPos, setDropdownPos] = useState({ top: 0, right: 0 });

  const buttonRef = useRef<HTMLButtonElement>(null);
  const panelRef = useRef<HTMLDivElement>(null);

  // Fermer au clic en dehors — vérifie le bouton ET le panel portal
  useEffect(() => {
    if (!open) return;
    const handleClickOutside = (e: MouseEvent) => {
      const target = e.target as Node;
      if (!target.isConnected) return;
      if (buttonRef.current?.contains(target)) return;
      if (panelRef.current?.contains(target)) return;
      setOpen(false);
    };
    // Délai pour ne pas capturer le clic d'ouverture
    const id = setTimeout(() => document.addEventListener("mousedown", handleClickOutside), 0);
    return () => {
      clearTimeout(id);
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [open]);

  // Recalculer position si scroll/resize pendant que le panel est ouvert
  useEffect(() => {
    if (!open) return;
    const recalculateDropdownPosition = () => {
      if (buttonRef.current) {
        const rect = buttonRef.current.getBoundingClientRect();
        setDropdownPos({ top: rect.bottom + 8, right: window.innerWidth - rect.right });
      }
    };
    window.addEventListener("scroll", recalculateDropdownPosition, true);
    window.addEventListener("resize", recalculateDropdownPosition);
    return () => {
      window.removeEventListener("scroll", recalculateDropdownPosition, true);
      window.removeEventListener("resize", recalculateDropdownPosition);
    };
  }, [open]);

  const toggleSavedSearchesPanel = () => {
    if (buttonRef.current) {
      const rect = buttonRef.current.getBoundingClientRect();
      setDropdownPos({ top: rect.bottom + 8, right: window.innerWidth - rect.right });
    }
    setOpen((prev) => !prev);
  };

  const fetchSavedSearchesFromApi = useCallback(async () => {
    if (!token) return;
    try {
      const savedSearchesResponse = await api.getSavedSearches(token);
      if (savedSearchesResponse.ok) {
        const savedSearches: SavedSearchRecord[] = await savedSearchesResponse.json();
        setSearches(savedSearches);
      }
    } catch { /* silently fail */ }
  }, [token]);

  useEffect(() => { if (open) fetchSavedSearchesFromApi(); }, [open, fetchSavedSearchesFromApi]);

  const saveCurrentSearch = async () => {
    if (!token || !newName.trim()) return;
    setSaving(true);
    setSaveError(null);
    try {
      const saveResponse = await api.createSavedSearch(token, {
        name: newName.trim(),
        query_json: { query, filters, searchMode, logicalQuery: searchMode === "advanced" ? logicalQuery : null },
      });
      if (saveResponse.ok) {
        setSaveSuccess(true);
        setNewName("");
        setShowSaveForm(false);
        fetchSavedSearchesFromApi();
        setTimeout(() => setSaveSuccess(false), 2000);
      } else {
        const apiErrorMessage = await saveResponse.json().then((d) => d.detail).catch(() => null);
        setSaveError(apiErrorMessage || `Erreur ${saveResponse.status}`);
      }
    } catch {
      setSaveError("Impossible de joindre le serveur");
    } finally {
      setSaving(false);
    }
  };

  const deleteSavedSearch = async (id: number) => {
    if (!token) return;
    try {
      await api.deleteSavedSearch(token, id);
      setSearches((prev) => prev.filter((savedSearch) => savedSearch.id !== id));
    } catch { /* silently fail */ }
  };

  const loadAndExecuteSavedSearch = (savedSearch: SavedSearchRecord) => {
    loadSearch(savedSearch.query_json);
    setOpen(false);
  };

  const hasCurrentSearch =
    query || Object.values(filters).some((filterValues) => filterValues.length > 0) || (Array.isArray(logicalQuery?.rules) && logicalQuery.rules.length > 0);

  if (typeof document === "undefined") {
    return (
      <button
        ref={buttonRef}
        data-testid="btn-saved-searches"
        className="flex items-center gap-2 px-4 py-2 text-sm font-bold text-foreground bg-secondary border border-border rounded-xl premium-shadow"
      >
        <Bookmark size={15} />
        {t("savedSearches")}
        <ChevronDown size={12} />
      </button>
    );
  }

  return (
    <>
      <button
        ref={buttonRef}
        data-testid="btn-saved-searches"
        onClick={toggleSavedSearchesPanel}
        className="flex items-center gap-2 px-4 py-2 text-sm font-bold text-foreground bg-secondary border border-border rounded-xl hover:bg-muted hover:border-highlight/50 transition-all premium-shadow"
      >
        <Bookmark size={15} className={saveSuccess ? "text-green-500" : ""} />
        {saveSuccess ? <Check size={15} className="text-green-500" /> : t("savedSearches")}
        <ChevronDown size={12} className={`transition-transform ${open ? "rotate-180" : ""}`} />
      </button>

      {createPortal(
        open ? (
          <div
            ref={panelRef}
            data-testid="saved-searches-panel"
            style={{
              position: "fixed",
              top: dropdownPos.top,
              right: dropdownPos.right,
              zIndex: 2147483647,
              width: "320px",
              backgroundColor: "hsl(var(--card))",
              border: "1px solid hsl(var(--border))",
              borderRadius: "1rem",
              boxShadow: "0 20px 60px -10px rgba(0,0,0,0.15)",
              padding: "1rem",
            }}
          >
            {hasCurrentSearch && (
              <div style={{ marginBottom: "1rem" }}>
                {showSaveForm ? (
                  <div style={{ display: "flex", flexDirection: "column", gap: "0.4rem" }}>
                    <div style={{ display: "flex", gap: "0.5rem" }}>
                      <input
                        data-testid="input-search-name"
                        type="text"
                        value={newName}
                        onChange={(e) => { setNewName(e.target.value); setSaveError(null); }}
                        placeholder={t("searchName")}
                        autoFocus
                        onKeyDown={(e) => e.key === "Enter" && saveCurrentSearch()}
                        className={`flex-1 px-3 py-2 text-sm rounded-lg border bg-background text-foreground focus:outline-none focus:ring-1 transition-all ${saveError ? "border-red-400 focus:border-red-400 focus:ring-red-300" : "border-border focus:border-highlight focus:ring-highlight/30"}`}
                      />
                      <button
                        data-testid="btn-save-confirm"
                        onClick={saveCurrentSearch}
                        disabled={saving || !newName.trim()}
                        className="px-3 py-2 bg-highlight text-white text-xs font-bold rounded-lg hover:brightness-110 transition-all disabled:opacity-60"
                      >
                        {saving ? (
                          <div className="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin" />
                        ) : (
                          <Check size={14} />
                        )}
                      </button>
                    </div>
                    {saveError && (
                      <p className="text-xs text-red-500 px-1">{saveError}</p>
                    )}
                  </div>
                ) : (
                  <button
                    data-testid="btn-show-save-form"
                    onClick={() => { setShowSaveForm(true); setSaveError(null); }}
                    className="w-full flex items-center gap-2 px-3 py-2.5 text-sm font-bold text-highlight bg-highlight/10 border border-highlight/20 rounded-xl hover:bg-highlight/20 transition-all"
                  >
                    <Plus size={15} />
                    {t("saveSearch")}
                  </button>
                )}
              </div>
            )}

            <div style={{ maxHeight: "16rem", overflowY: "auto" }}>
              {searches.length === 0 ? (
                <p className="text-xs text-muted-foreground text-center py-6 italic">
                  {t("noSavedSearches")}
                </p>
              ) : (
                searches.map((savedSearch) => (
                  <div
                    key={savedSearch.id}
                    className="group flex items-center gap-2 px-3 py-2.5 rounded-xl hover:bg-secondary transition-all"
                  >
                    <button
                      data-testid={`btn-load-search-${savedSearch.id}`}
                      onClick={() => loadAndExecuteSavedSearch(savedSearch)}
                      className="flex-1 text-left text-sm font-medium text-foreground hover:text-highlight transition-colors truncate"
                      title={savedSearch.name}
                    >
                      {savedSearch.name}
                    </button>
                    <button
                      data-testid={`btn-delete-search-${savedSearch.id}`}
                      onClick={() => deleteSavedSearch(savedSearch.id)}
                      className="opacity-0 group-hover:opacity-100 text-muted-foreground hover:text-red-500 transition-all"
                      title={t("deleteSavedSearch")}
                    >
                      <Trash2 size={13} />
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>
        ) : null,
        document.body
      )}
    </>
  );
}
