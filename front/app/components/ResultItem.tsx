"use client";

import type { SearchDoc } from "../types";
import { useTranslations } from "next-intl";

export default function ResultItem({ doc }: { doc: SearchDoc }) {
  const t = useTranslations();

  const title = doc.titre || doc.title || doc.naked_titre || t("noTitle");
  const description = doc.naked_resume || doc.naked_texte || doc.description || "";
  const url = doc.url || "#";
  const platform = doc.site_title || doc.platformID || "OpenEdition";
  const type = doc.type || "";
  const rawAuthors = doc.contributeurFacet_auteur || doc.contributeurFacetR_auteur;
  const authors = Array.isArray(rawAuthors) ? rawAuthors : rawAuthors ? [rawAuthors] : [];

  return (
    <article data-testid="result-item" className="bg-card border border-border rounded-2xl p-6 transition-all duration-300 hover:border-highlight/50 hover:shadow-lg hover:shadow-highlight/5 hover:-translate-y-1 slide-up-enter group">
      {/* Source badge row */}
      <div className="flex items-center gap-3 mb-4">
        <span className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-secondary border border-border text-xs font-bold text-secondary-foreground shadow-sm">
          <span className="w-2 h-2 rounded-full bg-highlight animate-pulse" />
          {platform}
        </span>
        {type && (
          <span className="inline-flex items-center px-3 py-1.5 rounded-full text-xs font-bold bg-highlight/10 text-highlight border border-highlight/20 shadow-sm">
            {type}
          </span>
        )}
      </div>

      {/* Title */}
      <h3 className="text-xl font-bold text-foreground mb-2 leading-tight font-serif tracking-tight">
        <a href={url} target="_blank" rel="noopener noreferrer"
          className="group-hover:text-highlight transition-colors decoration-highlight/30 underline-offset-4 hover:underline">
          {title}
        </a>
      </h3>

      {/* Authors */}
      {authors.length > 0 && (
        <p className="text-sm text-muted-foreground mb-3 font-semibold">
          {authors.slice(0, 3).join(" · ")}
          {authors.length > 3 && ` · ${t("andOthers")}`}
        </p>
      )}

      {/* Description */}
      {description && (
        <p className="text-sm text-foreground/80 leading-relaxed mb-5">
          {description.length > 280 ? `${description.substring(0, 280)}…` : description}
        </p>
      )}

      {/* View source link */}
      <a href={url} target="_blank" rel="noopener noreferrer"
        className="inline-flex items-center gap-1.5 text-sm font-bold text-highlight hover:text-primary transition-colors">
        {t("viewDocument")}
        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" className="group-hover:translate-x-1 transition-transform">
          <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
          <polyline points="15 3 21 3 21 9" />
          <line x1="10" y1="14" x2="21" y2="3" />
        </svg>
      </a>
    </article>
  );
}
