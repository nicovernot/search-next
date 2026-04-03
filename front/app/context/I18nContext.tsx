"use client";

import React, { createContext, useContext, useState, useEffect, useCallback } from "react";

type Translations = Record<string, string>;
const SUPPORTED_LANGS = ["fr", "en", "es", "it", "pt"];
const cache: Record<string, Translations> = {};

async function loadTranslations(lang: string): Promise<Translations> {
  if (cache[lang]) return cache[lang];
  try {
    const res = await fetch(`/locales/${lang}/translation.json`);
    cache[lang] = await res.json();
    return cache[lang];
  } catch {
    return {};
  }
}

function detectLang(): string {
  if (typeof navigator === "undefined") return "fr";
  const lang = navigator.language.split("-")[0];
  return SUPPORTED_LANGS.includes(lang) ? lang : "fr";
}

interface I18nContextValue {
  lang: string;
  setLang: (lang: string) => void;
  t: (key: string, vars?: Record<string, string | number>) => string;
  supportedLangs: string[];
}

const I18nContext = createContext<I18nContextValue | null>(null);

export function I18nProvider({ children }: { children: React.ReactNode }) {
  const [lang, setLangState] = useState("fr");
  const [translations, setTranslations] = useState<Translations>({});

  useEffect(() => {
    const detected = detectLang();
    setLangState(detected);
    loadTranslations(detected).then(setTranslations);
  }, []);

  const setLang = useCallback((newLang: string) => {
    setLangState(newLang);
    loadTranslations(newLang).then(setTranslations);
  }, []);

  const t = useCallback(
    (key: string, vars?: Record<string, string | number>) => {
      let str = translations[key] || key;
      if (vars) {
        for (const [k, v] of Object.entries(vars)) {
          str = str.replace(`{{${k}}}`, String(v));
        }
      }
      return str;
    },
    [translations]
  );

  return (
    <I18nContext.Provider value={{ lang, setLang, t, supportedLangs: SUPPORTED_LANGS }}>
      {children}
    </I18nContext.Provider>
  );
}

export function useTranslations() {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error("useTranslations must be used within I18nProvider");
  return ctx;
}
