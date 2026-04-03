"use client";

import React, { useState, useEffect, useRef, useCallback } from "react";
import { useSearch } from "../context/SearchContext";

interface AutocompleteInputProps {
  value: string;
  onChange: (val: string) => void;
  onSearch: () => void;
  placeholder?: string;
}

export default function AutocompleteInput({
  value,
  onChange,
  onSearch,
  placeholder,
}: AutocompleteInputProps) {
  const { suggestions, fetchSuggestions, loadingSuggestions } = useSearch();
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);
  const wrapperRef = useRef<HTMLDivElement>(null);
  const debounceTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Gérer le clic en dehors pour fermer les suggestions
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
        setShowSuggestions(false);
      }
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
        // On attend le prochain tick pour lancer la recherche avec la nouvelle valeur
        setTimeout(() => onSearch(), 0);
      } else {
        setShowSuggestions(false);
        onSearch();
      }
    } else if (e.key === "Escape") {
      setShowSuggestions(false);
    }
  };

  const handleSelectSuggestion = (suggestion: string) => {
    onChange(suggestion);
    setShowSuggestions(false);
    setTimeout(() => onSearch(), 0);
  };

  // Highlighting de la partie correspondante
  const renderSuggestion = (suggestion: string) => {
    const index = suggestion.toLowerCase().indexOf(value.toLowerCase());
    if (index === -1) return suggestion;
    
    return (
      <>
        {suggestion.substring(0, index)}
        <span className="font-bold text-[#f03603]">
          {suggestion.substring(index, index + value.length)}
        </span>
        {suggestion.substring(index + value.length)}
      </>
    );
  };

  return (
    <div ref={wrapperRef} className="relative flex-1 group">
      <input
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
        className="w-full px-4 py-3 rounded-lg border border-[#e6e4e2] bg-white text-[rgba(16,13,13,1)] placeholder-[#969493] focus:outline-none focus:border-[#f03603] focus:ring-1 focus:ring-[#f03603] transition-all text-base shadow-sm group-hover:border-[#969493]"
      />
      
      {loadingSuggestions && (
        <div className="absolute right-3 top-1/2 -translate-y-1/2">
          <div className="w-4 h-4 border-2 border-[#f03603] border-t-transparent rounded-full animate-spin"></div>
        </div>
      )}

      {showSuggestions && suggestions.length > 0 && (
        <ul className="absolute z-50 w-full mt-2 bg-white border border-[#e6e4e2] rounded-xl shadow-2xl overflow-hidden animate-in fade-in slide-in-from-top-2 duration-200">
          {suggestions.map((s, i) => (
            <li
              key={i}
              onClick={() => handleSelectSuggestion(s)}
              onMouseEnter={() => setActiveIndex(i)}
              className={`px-4 py-3 cursor-pointer transition-colors flex items-center gap-3 ${
                i === activeIndex ? "bg-gray-50 text-[#f03603]" : "text-gray-700 hover:bg-gray-50"
              }`}
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" className="text-gray-400">
                <circle cx="11" cy="11" r="8" />
                <path d="m21 21-4.35-4.35" />
              </svg>
              <span className="truncate">{renderSuggestion(s)}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
