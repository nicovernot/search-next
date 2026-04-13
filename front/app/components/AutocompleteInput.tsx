"use client";

import React, { useState, useEffect, useRef } from "react";
import { createPortal } from "react-dom";
import { useSearch } from "../context/SearchContext";

interface AutocompleteInputProps {
  value: string;
  onChange: (val: string) => void;
  onSearch?: () => void;
  placeholder?: string;
  inputClassName?: string;
  wrapperClassName?: string;
}

export default function AutocompleteInput({
  value,
  onChange,
  onSearch,
  placeholder,
  inputClassName,
  wrapperClassName,
}: AutocompleteInputProps) {
  const { suggestions, fetchSuggestions, loadingSuggestions } = useSearch();
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);
  const [dropdownRect, setDropdownRect] = useState<{ top: number; left: number; width: number }>({ top: 0, left: 0, width: 0 });
  const wrapperRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLUListElement>(null);
  const debounceTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Recalcule la position du dropdown à chaque ouverture ou resize/scroll
  const updateDropdownRect = () => {
    if (inputRef.current) {
      const r = inputRef.current.getBoundingClientRect();
      setDropdownRect({ top: r.bottom + 6, left: r.left, width: r.width });
    }
  };

  useEffect(() => {
    if (!showSuggestions) return;
    updateDropdownRect();
    window.addEventListener("resize", updateDropdownRect);
    window.addEventListener("scroll", updateDropdownRect, true);
    return () => {
      window.removeEventListener("resize", updateDropdownRect);
      window.removeEventListener("scroll", updateDropdownRect, true);
    };
  }, [showSuggestions]);

  // Fermer au clic en dehors — exclut le wrapper ET la liste portal
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      const target = event.target as Node;
      if (wrapperRef.current?.contains(target)) return;
      if (listRef.current?.contains(target)) return;
      setShowSuggestions(false);
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Debounce pour la récupération des suggestions
  useEffect(() => {
    if (debounceTimer.current) clearTimeout(debounceTimer.current);
    
    if (value.length >= 2) {
      debounceTimer.current = setTimeout(() => {
        fetchSuggestions(value);
      }, 300);
    } else {
      // setSuggestions([]); // Géré par fetchSuggestions si q court
    }

    return () => {
      if (debounceTimer.current) clearTimeout(debounceTimer.current);
    };
  }, [value, fetchSuggestions]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setShowSuggestions(true);
      setActiveIndex((prev) => (prev < suggestions.length - 1 ? prev + 1 : prev));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActiveIndex((prev) => (prev > 0 ? prev - 1 : -1));
    } else if (e.key === "Enter") {
      if (showSuggestions && activeIndex >= 0) {
        e.preventDefault();
        const selected = suggestions[activeIndex];
        onChange(selected);
        setShowSuggestions(false);
        if (onSearch) {
          // On attend le prochain tick pour lancer la recherche avec la nouvelle valeur
          setTimeout(() => onSearch(), 0);
        }
      } else {
        setShowSuggestions(false);
        onSearch?.();
      }
    } else if (e.key === "Escape") {
      setShowSuggestions(false);
    }
  };

  const handleSelectSuggestion = (suggestion: string) => {
    onChange(suggestion);
    setShowSuggestions(false);
    if (onSearch) {
      setTimeout(() => onSearch(), 0);
    }
  };

  // Highlighting de la partie correspondante
  const renderSuggestion = (suggestion: string) => {
    const index = suggestion.toLowerCase().indexOf(value.toLowerCase());
    if (index === -1) return suggestion;
    
    return (
      <>
        {suggestion.substring(0, index)}
        <span className="font-bold text-highlight">
          {suggestion.substring(index, index + value.length)}
        </span>
        {suggestion.substring(index + value.length)}
      </>
    );
  };

  const suggestionList =
    typeof document !== "undefined" && showSuggestions && suggestions.length > 0
      ? createPortal(
          <ul
            ref={listRef}
            style={{
              position: "fixed",
              top: dropdownRect.top,
              left: dropdownRect.left,
              width: dropdownRect.width,
              zIndex: 2147483647,
            }}
            className="bg-card border border-border rounded-2xl shadow-2xl overflow-hidden animate-fade-in premium-shadow"
          >
            {suggestions.map((s, i) => (
              <li
                key={i}
                onClick={() => handleSelectSuggestion(s)}
                onMouseEnter={() => setActiveIndex(i)}
                className={`px-5 py-3.5 cursor-pointer transition-colors flex items-center gap-4 border-b border-border/50 last:border-0 ${
                  i === activeIndex ? "bg-highlight/10 text-highlight" : "text-foreground hover:bg-secondary"
                }`}
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" className="text-gray-400">
                  <circle cx="11" cy="11" r="8" />
                  <path d="m21 21-4.35-4.35" />
                </svg>
                <span className="truncate">{renderSuggestion(s)}</span>
              </li>
            ))}
          </ul>,
          document.body
        )
      : null;

  return (
    <div ref={wrapperRef} className={wrapperClassName || "relative flex-1 group"}>
      <input
        ref={inputRef}
        type="text"
        value={value}
        onChange={(e) => {
          onChange(e.target.value);
          setShowSuggestions(true);
          setActiveIndex(-1);
        }}
        onFocus={() => {
          updateDropdownRect();
          setShowSuggestions(true);
        }}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        autoComplete="off"
        className={inputClassName || "w-full px-5 py-3.5 rounded-xl border border-border bg-card text-foreground placeholder-muted-foreground focus:outline-none focus:border-highlight focus:ring-2 focus:ring-highlight/30 transition-all text-base shadow-sm group-hover:border-highlight/50"}
      />

      {loadingSuggestions && (
        <div className="absolute right-4 top-1/2 -translate-y-1/2">
          <div className="w-5 h-5 border-2 border-highlight border-t-transparent rounded-full animate-spin"></div>
        </div>
      )}

      {suggestionList}
    </div>
  );
}
