"use client";

import { QueryBuilder, RuleGroupType, Field, type ValueEditorProps } from "react-querybuilder";
import "react-querybuilder/dist/query-builder.css";
import { useSearch } from "../context/SearchContext";
import { useTranslations } from "next-intl";
import { Search } from "lucide-react";
import AutocompleteInput from "./AutocompleteInput";
import { QB_FIELDS, QB_LABELS_MAP } from "../lib/qb-fields";

const DEFAULT_QUERY: RuleGroupType = {
  combinator: "and",
  rules: [],
};

function QueryBuilderAutocompleteValueEditor(props: ValueEditorProps) {
  const { suggestions, fetchSuggestions, loadingSuggestions } = useSearch();
  const currentValue = typeof props.value === "string" ? props.value : "";
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const placeholder = (props.schema as any)?.translations?.value?.label ?? "Value";

  return (
    <AutocompleteInput
      value={currentValue}
      onChange={(nextValue) => props.handleOnChange(nextValue)}
      placeholder={placeholder}
      wrapperClassName="relative w-full max-w-xs group"
      inputClassName="w-full rounded-md border border-border bg-card py-1 px-3 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-highlight/30 focus:border-highlight transition-all"
      suggestions={suggestions}
      onFetchSuggestions={fetchSuggestions}
      loadingSuggestions={loadingSuggestions}
    />
  );
}

export default function AdvancedQueryBuilder() {
  const t = useTranslations();
  const { executeSearch, setLogicalQuery, logicalQuery: contextLogicalQuery, searchFields } = useSearch();

  // Champs depuis l'API si disponibles, fallback sur QB_FIELDS hardcodés
  const fields: Field[] = (searchFields ?? QB_FIELDS.map((qbField) => qbField.name))
    .filter((name) => name in QB_LABELS_MAP)
    .map((name) => ({
      name,
      label: QB_LABELS_MAP[name] ? t(QB_LABELS_MAP[name]) : name,
    }));

  const operators = [
    { name: "=", label: t("qb_opEquals") },
    { name: "!=", label: t("qb_opNotEquals") },
    { name: "contains", label: t("qb_opContains") },
    { name: "doesNotContain", label: t("qb_opNotContains") },
    { name: "beginsWith", label: t("qb_opBeginsWith") },
    { name: "doesNotBeginWith", label: t("qb_opNotBeginsWith") },
    { name: "endsWith", label: t("qb_opEndsWith") },
    { name: "doesNotEndWith", label: t("qb_opNotEndsWith") },
  ];

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
          type="button"
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
          operators={operators}
          query={contextLogicalQuery ?? DEFAULT_QUERY}
          onQueryChange={(newQuery) => {
            setLogicalQuery(newQuery);
          }}
          translations={{
            addGroup: { label: t("qb_addGroup"), title: t("qb_addGroup") },
            addRule: { label: t("qb_addRule"), title: t("qb_addRule") },
            removeGroup: { label: t("qb_remove"), title: t("qb_remove") },
            removeRule: { label: t("qb_remove"), title: t("qb_remove") },
            combinators: { title: t("qb_logic") },
            fields: { title: t("qb_field") },
            operators: { title: t("qb_operator") },
            value: { title: t("qb_value") },
          }}
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

    </div>
  );
}
