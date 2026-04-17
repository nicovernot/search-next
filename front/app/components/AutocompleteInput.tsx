"use client";

import React, { useState, useEffect, useRef } from "react";
import { createPortal } from "react-dom";
import { useClickOutside } from "../hooks/useClickOutside";
import { useAnchoredPortal } from "../hooks/useAnchoredPortal";

interface AutocompleteInputProps {
  value: string;
  onChange: (val: string) => void;
  onSearch?: () => void;
  placeholder?: string;
  inputClassName?: string;
  wrapperClassName?: string;
  suggestions?: string[];
  onFetchSuggestions?: (q: string) => void;
  loadingSuggestions?: boolean;
}

export default function AutocompleteInput({
  value,
  onChange,
  onSearch,
  placeholder,
  inputClassName,
  wrapperClassName,
  suggestions = [],
  onFetchSuggestions,
  loadingSuggestions = false,
}: AutocompleteInputProps) {
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);
  const wrapperRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLUListElement>(null);
  const debounceTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const { style: dropdownStyle } = useAnchoredPortal(inputRef, showSuggestions, { align: "left", gap: 6 });
  useClickOutside([wrapperRef, listRef], () => setShowSuggestions(false));

  // Debounce pour la récupération des suggestions
  useEffect(() => {
    if (debounceTimer.current) clearTimeout(debounceTimer.current);

    if (value.length >= 2) {
      debounceTimer.current = setTimeout(() => {
        onFetchSuggestions?.(value);
      }, 300);
    }

    return () => {
      if (debounceTimer.current) clearTimeout(debounceTimer.current);
    };
  }, [value, onFetchSuggestions]);

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
        const selectedSuggestion = suggestions[activeIndex];
        onChange(selectedSuggestion);
        setShowSuggestions(false);
        if (onSearch) {
          // Attend le prochain tick pour lancer la recherche avec la nouvelle valeur
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
    const matchStartIndex = suggestion.toLowerCase().indexOf(value.toLowerCase());
    if (matchStartIndex === -1) return suggestion;

    return (
      <>
        {suggestion.substring(0, matchStartIndex)}
        <span className="font-bold text-highlight">
          {suggestion.substring(matchStartIndex, matchStartIndex + value.length)}
        </span>
        {suggestion.substring(matchStartIndex + value.length)}
      </>
    );
  };

  const suggestionPortal =
    typeof document !== "undefined" && showSuggestions && suggestions.length > 0
      ? createPortal(
          <ul
            ref={listRef}
            style={dropdownStyle}
            className="bg-card border border-border rounded-2xl shadow-2xl overflow-hidden animate-fade-in premium-shadow"
          >
            {suggestions.map((suggestion, i) => (
              <li
                key={i}
                onClick={() => handleSelectSuggestion(suggestion)}
                onMouseEnter={() => setActiveIndex(i)}
                className={`px-5 py-3.5 cursor-pointer transition-colors flex items-center gap-4 border-b border-border/50 last:border-0 ${
                  i === activeIndex ? "bg-highlight/10 text-highlight" : "text-foreground hover:bg-secondary"
                }`}
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" className="text-gray-400">
                  <circle cx="11" cy="11" r="8" />
                  <path d="m21 21-4.35-4.35" />
                </svg>
                <span className="truncate">{renderSuggestion(suggestion)}</span>
              </li>
            ))}
          </ul>,
          document.body,
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
        onFocus={() => setShowSuggestions(true)}
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

      {suggestionPortal}
    </div>
  );
}
