"use client";

import { useTranslations } from "next-intl";
import SearchBar from "../components/SearchBar";
import LanguageSelector from "../components/LanguageSelector";
import { ThemeToggle } from "../components/ThemeToggle";
import { useSearch } from "../context/SearchContext";
import { useAuth } from "../context/AuthContext";
import dynamic from "next/dynamic";
import AuthButtons from "../components/AuthButtons";
import AuthModal from "../components/AuthModal";
import SavedSearchesPanel from "../components/SavedSearchesPanel";

const AdvancedQueryBuilder = dynamic(() => import("../components/AdvancedQueryBuilder"), {
  ssr: false,
  loading: () => <div className="h-48 bg-muted animate-pulse rounded-2xl" />,
});

const ResultsList = dynamic(() => import("../components/ResultsList"), {
  ssr: false,
  loading: () => <div className="h-64 bg-muted animate-pulse rounded-2xl w-full" />,
});

const Facets = dynamic(() => import("../components/Facets"), {
  ssr: false,
  loading: () => <div className="h-96 bg-muted animate-pulse rounded-2xl w-full" />,
});

const PLATFORMS = [
  { label: "OpenEdition Books", color: "#4da9e4" },
  { label: "Revues.org", color: "#90c94d" },
  { label: "Hypothèses", color: "#f03603" },
  { label: "Calenda", color: "#f4ba41" },
  { label: "OpenEdition Journals", color: "#969493" },
];

export default function Home() {
  const t = useTranslations();
  const { results, loading, query, searchMode, setSearchMode } = useSearch();
  const { user, logout } = useAuth();
  const hasContent = loading || results.length > 0 || query.length > 0;

  return (
    <div className="min-h-screen bg-background text-foreground font-sans flex flex-col relative transition-colors duration-300">
      {/* Decorative blobs — fixed container to avoid overflow without overflow-hidden on root */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none" style={{ zIndex: 0 }}>
        <div className="absolute top-20 left-10 w-72 h-72 bg-primary/10 rounded-full blur-3xl opacity-60" />
        <div className="absolute top-40 right-20 w-96 h-96 bg-highlight/10 rounded-full blur-3xl opacity-50" />
        <div className="absolute bottom-20 left-1/3 w-80 h-80 bg-green-500/10 rounded-full blur-3xl opacity-40" />
      </div>

      {/* Header */}
      <header className="relative z-50 px-6 py-4 flex items-center justify-between glass animate-fade-in border-b-0 m-2 rounded-2xl">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-highlight flex items-center justify-center premium-shadow">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5">
              <circle cx="11" cy="11" r="8" /><path d="m21 21-4.35-4.35" />
            </svg>
          </div>
          <span className="font-bold text-foreground text-lg tracking-tight font-serif">
            <span className="text-highlight">Open</span>Edition Search
          </span>
        </div>
        <div className="flex items-center gap-3">
          {loading && (
            <div className="flex items-center gap-2 text-xs text-muted-foreground animate-fade-in">
              <div className="w-3.5 h-3.5 border-2 border-highlight border-t-transparent rounded-full animate-spin" />
            </div>
          )}
          <ThemeToggle />
          <LanguageSelector />
          {user ? (
            <>
              <SavedSearchesPanel />
              <button
                data-testid="btn-logout"
                onClick={logout}
                className="text-sm font-bold text-muted-foreground hover:text-foreground transition-colors px-3 py-1.5 rounded-lg hover:bg-muted"
              >
                {t("logout")}
              </button>
            </>
          ) : (
            <AuthButtons />
          )}
        </div>
      </header>

      {/* Hero content */}
      <div className={hasContent ? "hidden" : "flex flex-col items-center px-6 pb-8"}>
        <div className="w-full max-w-2xl text-center pt-[10vh]">
          <h2 className="hero-title text-5xl font-extrabold text-foreground mb-4 tracking-tight font-serif">
            {t("heroTitle")}{" "}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-highlight to-primary animate-pulse-glow">
              OpenEdition
            </span>
          </h2>
          <p className="hero-subtitle text-lg text-muted-foreground mb-8 max-w-xl mx-auto leading-relaxed">
            {t("heroSubtitle")}
          </p>
          <div className="hero-badges flex items-center justify-center gap-3 flex-wrap mb-10">
            {PLATFORMS.map((p) => (
              <span
                key={p.label}
                className="source-badge inline-flex items-center gap-2 px-4 py-2 rounded-full glass text-xs font-semibold text-foreground hover:scale-105 transition-transform premium-shadow cursor-default"
              >
                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: p.color }} />
                {p.label}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Search Mode Toggle */}
      <div className="max-w-2xl mx-auto px-6 mb-6 flex justify-center z-10 mt-6 md:mt-0">
        <div className="glass p-1.5 rounded-2xl flex premium-shadow relative z-20">
          <button
            onClick={() => setSearchMode("simple")}
            className={`px-6 py-2.5 rounded-xl text-sm font-bold transition-all ${
              searchMode === "simple"
                ? "bg-highlight text-white shadow-md scale-100"
                : "text-muted-foreground hover:text-foreground hover:bg-muted"
            }`}
          >
            {t("simpleSearch")}
          </button>
          <button
            onClick={() => setSearchMode("advanced")}
            className={`px-6 py-2.5 rounded-xl text-sm font-bold transition-all ${
              searchMode === "advanced"
                ? "bg-highlight text-white shadow-md scale-100"
                : "text-muted-foreground hover:text-foreground hover:bg-muted"
            }`}
          >
            {t("advancedSearch")}
          </button>
        </div>
      </div>

      {/* Search Component */}
      <div
        className={`relative z-30 transition-all duration-500 ease-in-out ${
          hasContent ? "px-6 pb-6" : "px-6 pb-12"
        }`}
      >
        <div
          className={
            hasContent
              ? "max-w-5xl mx-auto w-full glass rounded-3xl premium-shadow p-2"
              : "w-full max-w-3xl mx-auto"
          }
        >
          {searchMode === "simple" ? <SearchBar /> : <AdvancedQueryBuilder />}
        </div>
      </div>

      {/* Results */}
      <div
        className={`relative z-10 flex-1 transition-opacity duration-500 ${
          hasContent ? "opacity-100" : "opacity-0 hidden"
        }`}
      >
        <div className="max-w-5xl mx-auto w-full px-4 py-6 flex gap-6">
          <aside className="w-64 shrink-0 hidden md:block">
            <Facets />
          </aside>
          <div className="flex-1 min-w-0">
            <ResultsList />
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="relative z-10 py-6 px-6 mt-auto">
        <div className="max-w-5xl mx-auto flex items-center justify-center gap-3 text-xs text-muted-foreground">
          <span>Powered by</span>
          <span className="font-bold text-foreground">FastAPI</span>
          <span>+</span>
          <span className="font-bold text-foreground">Solr</span>
          <span>+</span>
          <span className="font-bold text-foreground bg-clip-text text-transparent bg-gradient-to-r from-gray-800 to-gray-500 dark:from-white dark:to-gray-400">
            Next.js
          </span>
        </div>
      </footer>

      {/* Modal auth — rendue via createPortal sur document.body, hors de tout stacking context */}
      <AuthModal />
    </div>
  );
}
