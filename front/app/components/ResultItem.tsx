"use client";

import React from "react";
import type { SearchDoc, PermissionInfo, PermissionStatus } from "../types";
import { useTranslations } from "next-intl";
import { Lock, LockOpen, Building2, HelpCircle } from "lucide-react";

function AccessBadge({ status, loading }: { status?: PermissionStatus; loading: boolean }) {
  const t = useTranslations();

  // Skeleton pendant le chargement (avant d'avoir un statut)
  if (loading && !status) {
    return (
      <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs bg-muted border border-border animate-pulse w-28 h-6" />
    );
  }

  if (!status) return null;

  const configs: Record<PermissionStatus, { icon: React.ReactNode; label: string; className: string }> = {
    open: {
      icon: <LockOpen size={11} />,
      label: t("access_open"),
      className: "bg-green-500/10 text-green-700 dark:text-green-400 border-green-500/20",
    },
    institutional: {
      icon: <Building2 size={11} />,
      label: t("access_institutional"),
      className: "bg-blue-500/10 text-blue-700 dark:text-blue-400 border-blue-500/20",
    },
    restricted: {
      icon: <Lock size={11} />,
      label: t("access_restricted"),
      className: "bg-orange-500/10 text-orange-700 dark:text-orange-400 border-orange-500/20",
    },
    unknown: {
      icon: <HelpCircle size={11} />,
      label: t("access_unknown"),
      className: "bg-muted text-muted-foreground border-border",
    },
  };

  const cfg = configs[status];

  return (
    <span
      data-testid={`perm-badge-${status}`}
      title={cfg.label}
      className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold border ${cfg.className}`}
    >
      {cfg.icon}
      {cfg.label}
    </span>
  );
}

const FORMAT_STYLES: Record<string, string> = {
  html: "bg-sky-500/10 text-sky-700 dark:text-sky-400 border-sky-500/20",
  epub: "bg-violet-500/10 text-violet-700 dark:text-violet-400 border-violet-500/20",
  pdf: "bg-rose-500/10 text-rose-700 dark:text-rose-400 border-rose-500/20",
};

export default function ResultItem({
  doc,
  permissionInfo,
  loadingPermissions,
}: {
  doc: SearchDoc;
  permissionInfo?: PermissionInfo;
  loadingPermissions: boolean;
}) {
  const t = useTranslations();

  const title = doc.titre || doc.title || doc.naked_titre || t("noTitle");
  const description = doc.naked_resume || doc.naked_texte || doc.description || "";
  const url = doc.url || "#";
  const platform = doc.site_title || doc.platformID || "OpenEdition";
  const type = doc.type || "";
  const rawAuthors = doc.contributeurFacet_auteur || doc.contributeurFacetR_auteur;
  const authors = Array.isArray(rawAuthors) ? rawAuthors : rawAuthors ? [rawAuthors] : [];
  const year = doc.anneedatepubli ? String(doc.anneedatepubli) : null;

  return (
    <article data-testid="result-item" className="bg-card border border-border rounded-2xl p-6 transition-all duration-300 hover:border-highlight/50 hover:shadow-lg hover:shadow-highlight/5 hover:-translate-y-1 slide-up-enter group">
      {/* Source badge row */}
      <div className="flex items-center gap-3 mb-4 flex-wrap">
        <span className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-secondary border border-border text-xs font-bold text-secondary-foreground shadow-sm">
          <span className="w-2 h-2 rounded-full bg-highlight animate-pulse" />
          {platform}
        </span>
        {type && (
          <span className="inline-flex items-center px-3 py-1.5 rounded-full text-xs font-bold bg-highlight/10 text-highlight border border-highlight/20 shadow-sm">
            {type}
          </span>
        )}
        {year && (
          <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold text-muted-foreground bg-muted border border-border">
            {year}
          </span>
        )}
        <AccessBadge status={permissionInfo?.status} loading={loadingPermissions} />
        {permissionInfo?.formats && permissionInfo.formats.length > 0 && permissionInfo.formats.map((fmt) => (
          <span
            key={fmt}
            className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider border ${FORMAT_STYLES[fmt.toLowerCase()] ?? "bg-muted text-muted-foreground border-border"}`}
          >
            {fmt.toUpperCase()}
          </span>
        ))}
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
