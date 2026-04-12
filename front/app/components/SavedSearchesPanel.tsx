"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { useTranslations } from "next-intl";
import { useAuth } from "../context/AuthContext";
import { useSearch } from "../context/SearchContext";
import { Bookmark, Trash2, ChevronDown, Plus, Check } from "lucide-react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8007";

interface SavedSearch {
  id: number;
  name: string;
  query_json: any;
  created_at: string;
}

export default function SavedSearchesPanel() {
  const t = useTranslations();
  const { token } = useAuth();
  const { query, filters, logicalQuery, searchMode, setQuery, setLogicalQuery, setSearchMode, executeSearch, clearFilters, addFilter } = useSearch();

  const [open, setOpen] = useState(false);
  const [searches, setSearches] = useState<SavedSearch[]>([]);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [newName, setNewName] = useState("");
  const [showSaveForm, setShowSaveForm] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // Fermer le panel au clic en dehors (sans backdrop fixed qui bloque les z-index)
  useEffect(() => {
    if (!open) return;
    const handleClickOutside = (e: MouseEvent) => {
      const target = e.target as Node;
      // If the target was removed from DOM during React re-render (e.g. btn-show-save-form),
      // it's disconnected — ignore it, the click was inside the component.
      if (!target.isConnected) return;
      if (containerRef.current && !containerRef.current.contains(target)) {
        setOpen(false);
      }
    };
    document.addEventListener("click", handleClickOutside);
    return () => document.removeEventListener("click", handleClickOutside);
  }, [open]);

  const fetchSearches = useCallback(async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API_BASE_URL}/saved-searches`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        setSearches(await res.json());
      }
    } catch {
      // silently fail
    }
  }, [token]);

  useEffect(() => {
    if (open) fetchSearches();
  }, [open, fetchSearches]);

  const handleSave = async () => {
    if (!token || !newName.trim()) return;
    setSaving(true);
    try {
      const queryPayload = {
        query,
        filters,
        searchMode,
        logicalQuery: searchMode === "advanced" ? logicalQuery : null,
      };
      const res = await fetch(`${API_BASE_URL}/saved-searches`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ name: newName.trim(), query_json: queryPayload }),
      });
      if (res.ok) {
        setSaveSuccess(true);
        setNewName("");
        setShowSaveForm(false);
        fetchSearches();
        setTimeout(() => setSaveSuccess(false), 2000);
      }
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!token) return;
    try {
      await fetch(`${API_BASE_URL}/saved-searches/${id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      setSearches((prev) => prev.filter((s) => s.id !== id));
    } catch {
      // silently fail
    }
  };

  const handleLoad = (s: SavedSearch) => {
    const { query: q, filters: f, searchMode: m, logicalQuery: lq } = s.query_json;
    if (q !== undefined) setQuery(q);
    if (m) setSearchMode(m);
    if (lq) setLogicalQuery(lq);
    // Restore filters
    clearFilters();
    if (f && typeof f === "object") {
      for (const [field, values] of Object.entries(f)) {
        for (const value of values as string[]) {
          addFilter(field, value);
        }
      }
    }
    setOpen(false);
    setTimeout(() => executeSearch(), 50);
  };

  const hasCurrentSearch = query || Object.values(filters).some((v) => v.length > 0) || logicalQuery?.rules?.length > 0;

  return (
    <div className="relative" ref={containerRef}>
      <button
        data-testid="btn-saved-searches"
        onClick={() => setOpen(!open)}
        className="flex items-center gap-2 px-4 py-2 text-sm font-bold text-foreground bg-secondary border border-border rounded-xl hover:bg-muted hover:border-highlight/50 transition-all premium-shadow"
      >
        <Bookmark size={15} className={saveSuccess ? "text-green-500" : ""} />
        {saveSuccess ? <Check size={15} className="text-green-500" /> : t("savedSearches")}
        <ChevronDown size={12} className={`transition-transform ${open ? "rotate-180" : ""}`} />
      </button>

      {open && (
        <>
          <div data-testid="saved-searches-panel" className="absolute right-0 top-12 z-40 w-80 bg-card border border-border rounded-2xl premium-shadow animate-fade-in p-4">
            {/* Save current search */}
            {hasCurrentSearch && (
              <div className="mb-4">
                {showSaveForm ? (
                  <div className="flex gap-2">
                    <input
                      data-testid="input-search-name"
                      type="text"
                      value={newName}
                      onChange={(e) => setNewName(e.target.value)}
                      placeholder={t("searchName")}
                      autoFocus
                      onKeyDown={(e) => e.key === "Enter" && handleSave()}
                      className="flex-1 px-3 py-2 text-sm rounded-lg border border-border bg-background text-foreground focus:outline-none focus:border-highlight focus:ring-1 focus:ring-highlight/30 transition-all"
                    />
                    <button
                      data-testid="btn-save-confirm"
                      onClick={handleSave}
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
                ) : (
                  <button
                    data-testid="btn-show-save-form"
                    onClick={() => setShowSaveForm(true)}
                    className="w-full flex items-center gap-2 px-3 py-2.5 text-sm font-bold text-highlight bg-highlight/10 border border-highlight/20 rounded-xl hover:bg-highlight/20 transition-all"
                  >
                    <Plus size={15} />
                    {t("saveSearch")}
                  </button>
                )}
              </div>
            )}

            {/* List */}
            <div className="space-y-1 max-h-64 overflow-y-auto">
              {searches.length === 0 ? (
                <p className="text-xs text-muted-foreground text-center py-6 italic">
                  {t("noSavedSearches")}
                </p>
              ) : (
                searches.map((s) => (
                  <div
                    key={s.id}
                    className="group flex items-center gap-2 px-3 py-2.5 rounded-xl hover:bg-secondary transition-all"
                  >
                    <button
                      data-testid={`btn-load-search-${s.id}`}
                      onClick={() => handleLoad(s)}
                      className="flex-1 text-left text-sm font-medium text-foreground hover:text-highlight transition-colors truncate"
                      title={s.name}
                    >
                      {s.name}
                    </button>
                    <button
                      data-testid={`btn-delete-search-${s.id}`}
                      onClick={() => handleDelete(s.id)}
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
        </>
      )}
    </div>
  );
}
