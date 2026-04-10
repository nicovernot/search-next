"use client";

import { useTranslations } from "../context/I18nContext";

const LANG_LABELS: Record<string, string> = {
  fr: "Français",
  en: "English",
  es: "Español",
  it: "Italiano",
  pt: "Português",
};

export default function LanguageSelector() {
  const { lang, setLang, supportedLangs } = useTranslations();

  return (
    <select
      value={lang}
      onChange={(e) => setLang(e.target.value)}
      className="text-sm font-bold border border-border rounded-xl px-4 py-2 bg-secondary text-foreground focus:outline-none focus:border-highlight focus:ring-2 focus:ring-highlight/30 cursor-pointer appearance-none premium-shadow hover:bg-muted transition-all"
    >
      {supportedLangs.map((l) => (
        <option key={l} value={l}>{LANG_LABELS[l] || l}</option>
      ))}
    </select>
  );
}
