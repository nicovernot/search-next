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
    <div className="bg-white border border-[#e6e4e2] rounded-2xl shadow-xl p-6 mb-8 animate-in fade-in slide-in-from-top-4 duration-500">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-semibold text-gray-900 border-l-4 border-[#f03603] pl-4">
          Constructeur de Requête Logique
        </h3>
        <button
          onClick={handleSearch}
          className="flex items-center gap-2 px-6 py-2.5 bg-[#f03603] text-white rounded-full font-medium hover:bg-[#d23003] transition-all shadow-lg hover:shadow-[#f0360333] active:scale-95"
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
            ruleGroup: "bg-gray-50 border border-gray-100 rounded-xl p-4 transition-all hover:border-gray-200",
            combinators: "rounded-md border-gray-300 py-1 px-2 text-sm focus:ring-[#f03603] focus:border-[#f03603]",
            addRule: "text-xs font-medium bg-white border border-gray-200 px-3 py-1.5 rounded-md hover:bg-gray-50 transition-colors flex items-center gap-1",
            addGroup: "text-xs font-medium bg-white border border-gray-200 px-3 py-1.5 rounded-md hover:bg-gray-50 transition-colors flex items-center gap-1",
            fields: "rounded-md border-gray-300 py-1 px-2 text-sm focus:ring-[#f03603] focus:border-[#f03603]",
            operators: "rounded-md border-gray-300 py-1 px-2 text-sm focus:ring-[#f03603] focus:border-[#f03603]",
            value: "rounded-md border-gray-300 py-1 px-3 text-sm focus:ring-[#f03603] focus:border-[#f03603] w-full max-w-xs",
            removeRule: "text-gray-400 hover:text-red-500 transition-colors p-1",
            removeGroup: "text-gray-400 hover:text-red-500 transition-colors p-1",
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
            background: #e6e4e2;
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
