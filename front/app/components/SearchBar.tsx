"use client";

import { useSearch } from "../context/SearchContext";
import { useTranslations } from "next-intl";
import AutocompleteInput from "./AutocompleteInput";

export default function SearchBar() {
  const t = useTranslations();
  const { query, setQuery, executeSearch, suggestions, fetchSuggestions, loadingSuggestions } = useSearch();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    executeSearch();
  };

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="flex gap-2 w-full max-w-3xl mx-auto items-center">
        <AutocompleteInput
          value={query}
          onChange={setQuery}
          onSearch={executeSearch}
          placeholder={t("searchPlaceholder")}
          suggestions={suggestions}
          onFetchSuggestions={fetchSuggestions}
          loadingSuggestions={loadingSuggestions}
        />
        <button
          type="submit"
          className="px-6 py-[11px] bg-highlight text-white rounded-xl font-bold hover:brightness-110 transition-all flex items-center gap-2 whitespace-nowrap premium-shadow hover:scale-105 active:scale-95"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <circle cx="11" cy="11" r="8" />
            <path d="m21 21-4.35-4.35" />
          </svg>
          <span className="hidden sm:inline">{t("searchButton")}</span>
        </button>
      </div>
    </form>
  );
}
