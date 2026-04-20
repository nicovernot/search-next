"use client";

import { useLocale } from "next-intl";
import { useRouter, usePathname } from "../../i18n/navigation";
import { routing } from "../../i18n/routing";

const LANG_LABELS: Record<string, string> = {
  fr: "Français",
  en: "English",
  es: "Español",
  it: "Italiano",
  pt: "Português",
  de: "Deutsch",
};

export default function LanguageSelector() {
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();

  return (
    <select
      value={locale}
      onChange={(e) => router.replace(pathname, { locale: e.target.value })}
      className="text-sm font-bold border border-border rounded-xl px-4 py-2 bg-secondary text-foreground focus:outline-none focus:border-highlight focus:ring-2 focus:ring-highlight/30 cursor-pointer appearance-none premium-shadow hover:bg-muted transition-all"
    >
      {routing.locales.map((locale) => (
        <option key={locale} value={locale}>
          {LANG_LABELS[locale] || locale}
        </option>
      ))}
    </select>
  );
}
