"use client";

import SearchBar from "./components/SearchBar";
import LanguageSelector from "./components/LanguageSelector";
import { useSearch } from "./context/SearchContext";
import dynamic from "next/dynamic";

const AdvancedQueryBuilder = dynamic(() => import("./components/AdvancedQueryBuilder"), {
  ssr: false,
  loading: () => <div className="h-48 bg-gray-100 animate-pulse rounded-2xl" />
});

const ResultsList = dynamic(() => import("./components/ResultsList"), {
  ssr: false,
  loading: () => <div className="h-64 bg-gray-100 animate-pulse rounded-2xl w-full" />
});

const Facets = dynamic(() => import("./components/Facets"), {
  ssr: false,
  loading: () => <div className="h-96 bg-gray-100 animate-pulse rounded-2xl w-full" />
});

const PLATFORMS = [
  { label: "OpenEdition Books", color: "#4da9e4" },
  { label: "Revues.org", color: "#90c94d" },
  { label: "Hypothèses", color: "#f03603" },
  { label: "Calenda", color: "#f4ba41" },
  { label: "OpenEdition Journals", color: "#969493" },
];

export default function Home() {
  const { results, loading, query, searchMode, setSearchMode } = useSearch();
  const hasContent = loading || results.length > 0 || query.length > 0;

  return (
    <div className="min-h-screen bg-[#f9f6f4] bb-grid-pattern text-[rgba(16,13,13,1)] font-sans flex flex-col relative overflow-hidden">
      {/* Decorative blobs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-72 h-72 bg-[#f03603]/5 rounded-full blur-3xl" />
        <div className="absolute top-40 right-20 w-96 h-96 bg-[#4da9e4]/5 rounded-full blur-3xl" />
        <div className="absolute bottom-20 left-1/3 w-80 h-80 bg-[#90c94d]/5 rounded-full blur-3xl" />
      </div>

      {/* Header */}
      <header className="relative z-10 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-[#f03603] flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5">
              <circle cx="11" cy="11" r="8" /><path d="m21 21-4.35-4.35" />
            </svg>
          </div>
          <span className="font-bold text-[rgba(16,13,13,1)] text-sm">
            <span className="text-[#f03603]">Open</span>Edition Search
          </span>
        </div>
        <LanguageSelector />
      </header>

      {/* Hero content — caché mais monté quand hasContent */}
      <div className={hasContent ? "hidden" : "flex flex-col items-center px-6 pb-8 relative z-10"}>
        <div className="w-full max-w-2xl text-center pt-[10vh]">
          <h2 className="hero-title text-4xl font-bold text-[rgba(16,13,13,1)] mb-3 tracking-tight">
            Rechercher dans <span className="text-[#f03603]">OpenEdition</span>
          </h2>
          <p className="hero-subtitle text-lg text-[#4a4848] mb-6 max-w-xl mx-auto">
            Accédez à des milliers de publications en sciences humaines et sociales.
          </p>
          <div className="hero-badges flex items-center justify-center gap-2 flex-wrap mb-8">
            {PLATFORMS.map((p) => (
              <span key={p.label}
                className="source-badge inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white border border-[#e6e4e2] text-xs font-medium text-[#4a4848]">
                <span className="w-2 h-2 rounded-full" style={{ backgroundColor: p.color }} />
                {p.label}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Search Mode Toggle */}
      <div className="max-w-2xl mx-auto px-6 mb-4 flex justify-center">
        <div className="bg-white/50 backdrop-blur-sm p-1 rounded-xl border border-[#e6e4e2] flex shadow-sm">
          <button
            onClick={() => setSearchMode("simple")}
            className={`px-6 py-2 rounded-lg text-sm font-medium transition-all ${
              searchMode === "simple"
                ? "bg-white text-[#f03603] shadow-sm"
                : "text-gray-500 hover:text-gray-700"
            }`}
          >
            Recherche Simple
          </button>
          <button
            onClick={() => setSearchMode("advanced")}
            className={`px-6 py-2 rounded-lg text-sm font-medium transition-all ${
              searchMode === "advanced"
                ? "bg-white text-[#f03603] shadow-sm"
                : "text-gray-500 hover:text-gray-700"
            }`}
          >
            Recherche Avancée
          </button>
        </div>
      </div>

      {/* Search Component — unique instance, sticky quand hasContent */}
      <div className={`relative z-30 transition-all duration-200 ${
        hasContent
          ? "sticky top-0 bg-[#f9f6f4]/90 backdrop-blur-sm border-b border-[#e6e4e2] px-6 py-3"
          : "px-6 pb-12"
      }`}>
        <div className={hasContent ? "max-w-5xl mx-auto w-full" : "w-full max-w-2xl mx-auto"}>
          {searchMode === "simple" ? (
            <SearchBar />
          ) : (
            <AdvancedQueryBuilder />
          )}
        </div>
      </div>

      {/* Results */}
      <div className={`relative z-10 flex-1 ${hasContent ? "block" : "hidden"}`}>
        <div className="max-w-5xl mx-auto w-full px-4 py-6 flex gap-6">
          <aside className="w-56 shrink-0 hidden md:block">
            <Facets />
          </aside>
          <div className="flex-1 min-w-0">
            <ResultsList />
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="relative z-10 border-t border-[#e6e4e2] py-4 px-6">
        <div className="max-w-5xl mx-auto flex items-center justify-center gap-2 text-xs text-[#969493]">
          <span>Powered by</span>
          <span className="font-semibold text-[rgba(16,13,13,1)]">FastAPI</span>
          <span>+</span>
          <span className="font-semibold text-[rgba(16,13,13,1)]">Solr</span>
          <span>+</span>
          <span className="font-semibold text-[rgba(16,13,13,1)]">Next.js</span>
        </div>
      </footer>
    </div>
  );
}
