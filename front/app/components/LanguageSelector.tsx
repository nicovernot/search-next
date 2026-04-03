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
      className="text-sm border border-[#e6e4e2] rounded px-2 py-1 bg-white text-[#4a4848] focus:outline-none focus:border-[#f03603] cursor-pointer"
    >
      {supportedLangs.map((l) => (
        <option key={l} value={l}>{LANG_LABELS[l] || l}</option>
      ))}
    </select>
  );
}
