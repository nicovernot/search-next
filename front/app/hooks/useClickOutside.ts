/**
 * Ferme un élément flottant quand l'utilisateur clique en dehors des zones autorisées.
 * Intention : centraliser le pattern click-outside au lieu de le dupliquer dans chaque composant portal.
 * Résultat : onClose est appelé au prochain mousedown extérieur aux refs passées, seulement si enabled=true.
 */
import { type RefObject, useEffect } from "react";

export function useClickOutside(
  refs: RefObject<HTMLElement | null>[],
  onClose: () => void,
  enabled = true,
) {
  useEffect(() => {
    if (!enabled) return;
    const handler = (e: MouseEvent) => {
      const target = e.target as Node;
      if (!target.isConnected) return;
      if (refs.some((ref) => ref.current?.contains(target))) return;
      onClose();
    };
    // setTimeout(0) : évite de capturer le clic d'ouverture dans le même tick d'event loop
    const id = setTimeout(() => document.addEventListener("mousedown", handler), 0);
    return () => {
      clearTimeout(id);
      document.removeEventListener("mousedown", handler);
    };
  }, [refs, onClose, enabled]);
}
