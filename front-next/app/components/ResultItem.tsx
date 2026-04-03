"use client";

import type { SearchDoc } from "../types";
import { useTranslations } from "../context/I18nContext";

export default function ResultItem({ doc }: { doc: SearchDoc }) {
  const { t } = useTranslations();

  const title = doc.titre || doc.title || doc.naked_titre || t("noTitle");
  const description = doc.naked_resume || doc.naked_texte || doc.description || "";
  const url = doc.url || "#";
  const platform = doc.site_title || doc.platformID || "OpenEdition";
  const type = doc.type || "";
  const rawAuthors = doc.contributeurFacet_auteur || doc.contributeurFacetR_auteur;
  const authors = Array.isArray(rawAuthors) ? rawAuthors : rawAuthors ? [rawAuthors] : [];

  return (
    <article className="bg-white border border-[#e6e4e2] rounded-lg p-5 hover:border-[#f03603]/40 hover:shadow-sm transition-all duration-200 slide-up-enter">
      {/* Source badge row — style FindingCard */}
      <div className="flex items-center gap-2 mb-3">
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#f9f6f4] border border-[#e6e4e2] text-xs font-medium text-[#4a4848]">
          <span className="w-1.5 h-1.5 rounded-full bg-[#f03603]" />
          {platform}
        </span>
        {type && (
          <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-[#f03603]/8 text-[#f03603] border border-[#f03603]/20">
            {type}
          </span>
        )}
      </div>

      {/* Title */}
      <h3 className="text-base font-semibold text-[rgba(16,13,13,1)] mb-1.5 leading-snug">
        <a href={url} target="_blank" rel="noopener noreferrer"
          className="hover:text-[#f03603] transition-colors">
          {title}
        </a>
      </h3>

      {/* Authors — style relevance line */}
      {authors.length > 0 && (
        <p className="text-xs text-[#969493] mb-2 font-medium">
          {authors.slice(0, 3).join(" · ")}
          {authors.length > 3 && ` · ${t("andOthers")}`}
        </p>
      )}

      {/* Description — style summary */}
      {description && (
        <p className="text-sm text-[#4a4848] leading-relaxed mb-4">
          {description.length > 280 ? `${description.substring(0, 280)}…` : description}
        </p>
      )}

      {/* View source link — style FindingCard */}
      <a href={url} target="_blank" rel="noopener noreferrer"
        className="inline-flex items-center gap-1 text-xs font-medium text-[#f03603] hover:underline">
        {t("viewDocument")}
        <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
          <polyline points="15 3 21 3 21 9" />
          <line x1="10" y1="14" x2="21" y2="3" />
        </svg>
      </a>
    </article>
  );
}
