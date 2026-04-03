"use client";

import { useState, useEffect, useCallback } from "react";

type Translations = Record<string, string>;

const cache: Record<string, Translations> = {};

const SUPPORTED_LANGS = ["fr", "en", "es", "it", "pt"];

function detectLang(): string {
  if (typeof navigator === "undefined") return "en";
  const lang = navigator.language.split("-")[0];
  return SUPPORTED_LANGS.includes(lang) ? lang : "en";
}

async function loadTranslations(lang: string): Promise<Translations> {
  if (cache[lang]) return cache[lang];
  try {
    const res = await fetch(`/locales/${lang}/translation.json`);
    const data = await res.json();
    cache[lang] = data;
    return data;
  } catch {
    return {};
  }
}

export function useTranslations() {
  const [lang, setLangState] = useState("en");
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

  return { t, lang, setLang, supportedLangs: SUPPORTED_LANGS };
}
