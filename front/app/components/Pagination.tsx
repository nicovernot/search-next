"use client";

import { useSearch } from "../context/SearchContext";
import { useTranslations } from "next-intl";

export default function Pagination({ total }: { total: number }) {
  const t = useTranslations();
  const { pagination, setPage } = useSearch();

  const pageSize = pagination.size || 10;
  const currentPage = Math.floor((pagination.from || 0) / pageSize) + 1;
  const totalPages = Math.ceil(total / pageSize);

  if (totalPages <= 1) return null;

  const getPages = () => {
    const pages: (number | "...")[] = [];
    if (totalPages <= 7) {
      for (let i = 1; i <= totalPages; i++) pages.push(i);
    } else if (currentPage <= 4) {
      for (let i = 1; i <= 5; i++) pages.push(i);
      pages.push("...", totalPages);
    } else if (currentPage >= totalPages - 3) {
      pages.push(1, "...");
      for (let i = totalPages - 4; i <= totalPages; i++) pages.push(i);
    } else {
      pages.push(1, "...");
      for (let i = currentPage - 1; i <= currentPage + 1; i++) pages.push(i);
      pages.push("...", totalPages);
    }
    return pages;
  };

  const go = (page: number) => {
    setPage(page);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <nav className="flex items-center justify-center gap-1 mt-6">
      <button
        onClick={() => go(currentPage - 1)}
        disabled={currentPage === 1}
        className="px-3 py-1.5 text-sm rounded border border-[#e6e4e2] disabled:opacity-40 hover:border-[#f03603] hover:text-[#f03603] transition-colors"
      >
        ← {t("previous")}
      </button>

      {getPages().map((page, i) =>
        page === "..." ? (
          <span key={`e${i}`} className="px-2 text-[#969493]">…</span>
        ) : (
          <button
            key={page}
            onClick={() => go(page as number)}
            className={`w-8 h-8 text-sm rounded border transition-colors ${
              currentPage === page
                ? "bg-[#f03603] text-white border-[#f03603]"
                : "border-[#e6e4e2] hover:border-[#f03603] hover:text-[#f03603]"
            }`}
          >
            {page}
          </button>
        )
      )}

      <button
        onClick={() => go(currentPage + 1)}
        disabled={currentPage === totalPages}
        className="px-3 py-1.5 text-sm rounded border border-[#e6e4e2] disabled:opacity-40 hover:border-[#f03603] hover:text-[#f03603] transition-colors"
      >
        {t("next")} →
      </button>
    </nav>
  );
}
