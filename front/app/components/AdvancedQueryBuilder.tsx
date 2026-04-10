"use client";

import React, { useState } from "react";
import { QueryBuilder, RuleGroupType, Field } from "react-querybuilder";
import "react-querybuilder/dist/query-builder.css";
import { useSearch } from "../context/SearchContext";
import { useTranslations } from "../context/I18nContext";
import { Search, Trash2, Plus, ChevronDown } from "lucide-react";

const fields: Field[] = [
  { name: "titre", label: "Titre" },
  { name: "author", label: "Auteur" },
  { name: "naked_texte", label: "Texte intégral" },
  { name: "disciplinary_field", label: "Sujet / Mots-clés" },
];

export default function AdvancedQueryBuilder() {
  const { t } = useTranslations();
  const { executeSearch, setLogicalQuery } = useSearch();
  const [query, setQuery] = useState<RuleGroupType>({
    combinator: "and",
    rules: [],
  });

  const handleSearch = () => {
    setLogicalQuery(query);
    executeSearch();
  };

  return (
    <div className="bg-card border border-border rounded-2xl shadow-xl p-6 mb-8 animate-fade-in premium-shadow">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-bold text-foreground border-l-4 border-highlight pl-4 font-serif">
          Constructeur de Requête Logique
        </h3>
        <button
          onClick={handleSearch}
          className="flex items-center gap-2 px-6 py-2.5 bg-highlight text-white rounded-xl font-bold hover:brightness-110 transition-all premium-shadow active:scale-95"
        >
          <Search size={18} />
          {t("searchButton")}
        </button>
      </div>

      <div className="query-builder-premium">
        <QueryBuilder
          fields={fields}
          query={query}
          onQueryChange={(q) => {
            setQuery(q);
            setLogicalQuery(q);
          }}
          translations={{
            addGroup: "+ Groupe",
            addRule: "+ Règle",
            removeGroup: "Supprimer",
            removeRule: "Supprimer",
            combinators: { label: "Logique" },
            fields: { label: "Champ" },
            operators: { label: "Opérateur" },
            value: { label: "Valeur" },
          } as any}
          controlClassnames={{
            queryBuilder: "space-y-4",
            ruleGroup: "bg-secondary/40 border border-border rounded-xl p-4 transition-all hover:border-highlight/30",
            combinators: "rounded-md border-border bg-card py-1 px-2 text-sm focus:ring-highlight focus:border-highlight text-foreground",
            addRule: "text-xs font-bold bg-secondary text-foreground border border-border px-3 py-1.5 rounded-md hover:bg-muted transition-colors flex items-center gap-1 premium-shadow",
            addGroup: "text-xs font-bold bg-secondary text-foreground border border-border px-3 py-1.5 rounded-md hover:bg-muted transition-colors flex items-center gap-1 premium-shadow",
            fields: "rounded-md border-border bg-card py-1 px-2 text-sm focus:ring-highlight focus:border-highlight text-foreground",
            operators: "rounded-md border-border bg-card py-1 px-2 text-sm focus:ring-highlight focus:border-highlight text-foreground",
            value: "rounded-md border-border bg-card py-1 px-3 text-sm focus:ring-highlight focus:border-highlight text-foreground w-full max-w-xs",
            removeRule: "text-muted-foreground hover:text-destructive transition-colors p-1",
            removeGroup: "text-muted-foreground hover:text-destructive transition-colors p-1",
          }}
        />
      </div>

      <style jsx global>{`
        .query-builder-premium .ruleGroup {
            position: relative;
        }
        .query-builder-premium .ruleGroup:before {
            content: '';
            position: absolute;
            left: -20px;
            top: 20px;
            bottom: 20px;
            width: 2px;
            background: hsl(var(--border));
        }
        .query-builder-premium .rule {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 8px 0;
        }
      `}</style>
    </div>
  );
}
