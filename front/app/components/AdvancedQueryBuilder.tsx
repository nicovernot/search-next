"use client";

import React, { useState, useEffect } from "react";
import { QueryBuilder, RuleGroupType, Field } from "react-querybuilder";
import "react-querybuilder/dist/query-builder.css";
import { useSearch } from "../context/SearchContext";
import { useTranslations } from "next-intl";
import { Search } from "lucide-react";
import AutocompleteInput from "./AutocompleteInput";

interface QueryBuilderValueEditorProps {
  value?: unknown;
  handleOnChange: (value: string) => void;
  schema?: {
    translations?: {
      value?: {
        label?: string;
      };
    };
  };
}

function QueryBuilderAutocompleteValueEditor(props: QueryBuilderValueEditorProps) {
  const currentValue = typeof props.value === "string" ? props.value : "";

  return (
    <AutocompleteInput
      value={currentValue}
      onChange={(nextValue) => props.handleOnChange(nextValue)}
      placeholder={props.schema?.translations?.value?.label || "Value"}
      wrapperClassName="relative w-full max-w-xs group"
      inputClassName="w-full rounded-md border border-border bg-card py-1 px-3 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-highlight/30 focus:border-highlight transition-all"
    />
  );
}

export default function AdvancedQueryBuilder() {
  const t = useTranslations();
  const { executeSearch, setLogicalQuery, logicalQuery: contextLogicalQuery } = useSearch();

  const fields: Field[] = [
    { name: "titre", label: t("qb_fieldTitle") },
    { name: "author", label: t("qb_fieldAuthor") },
    { name: "naked_texte", label: t("qb_fieldFullText") },
    { name: "disciplinary_field", label: t("qb_fieldKeywords") },
  ];
  const [query, setQuery] = useState<RuleGroupType>({
    combinator: "and",
    rules: [],
  });

  // Sync local builder state when a saved search restores logicalQuery
  useEffect(() => {
    if (contextLogicalQuery?.rules) {
      setQuery(contextLogicalQuery as RuleGroupType);
    }
  }, [contextLogicalQuery]);

  const handleSearch = () => {
    // setLogicalQuery synced via onQueryChange — executeSearch lit depuis latestRef
    executeSearch();
  };

  return (
    <div className="bg-card border border-border rounded-2xl shadow-xl p-6 mb-8 animate-fade-in premium-shadow">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-bold text-foreground border-l-4 border-highlight pl-4 font-serif">
          {t("queryBuilderTitle")}
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
            addGroup: t("qb_addGroup"),
            addRule: t("qb_addRule"),
            removeGroup: t("qb_remove"),
            removeRule: t("qb_remove"),
            combinators: { label: t("qb_logic") },
            fields: { label: t("qb_field") },
            operators: { label: t("qb_operator") },
            value: { label: t("qb_value") },
          } as const}
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
          controlElements={{
            valueEditor: QueryBuilderAutocompleteValueEditor,
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
