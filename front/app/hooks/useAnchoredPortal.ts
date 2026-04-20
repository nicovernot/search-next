/**
 * Calcule et maintient la position fixed d'un élément ancré sur un autre (dropdown/popover).
 * Intention : éviter de dupliquer le pattern getBoundingClientRect + scroll/resize dans chaque composant portal.
 * Résultat : retourne { style, update } — style est à appliquer sur l'élément flottant,
 *            update permet un recalcul immédiat (utile pour batcher la mise à jour avec l'ouverture).
 */
import { type CSSProperties, type RefObject, useState, useCallback, useEffect } from "react";

interface AnchoredPortalOptions {
  /** Alignement horizontal : 'left' aligne le bord gauche + width, 'right' aligne le bord droit. Défaut : 'left'. */
  align?: "left" | "right";
  /** Espace vertical entre l'ancre et l'élément flottant, en pixels. Défaut : 8. */
  gap?: number;
}

export function useAnchoredPortal(
  anchorRef: RefObject<HTMLElement | null>,
  open: boolean,
  options: AnchoredPortalOptions = {},
) {
  const { align = "left", gap = 8 } = options;
  const [style, setStyle] = useState<CSSProperties>({});

  const update = useCallback(() => {
    if (!anchorRef.current) return;
    const rect = anchorRef.current.getBoundingClientRect();
    setStyle(
      align === "right"
        ? { position: "fixed", top: rect.bottom + gap, right: window.innerWidth - rect.right, zIndex: 2147483647 }
        : { position: "fixed", top: rect.bottom + gap, left: rect.left, width: rect.width, zIndex: 2147483647 },
    );
  }, [anchorRef, align, gap]);

  // Recalcule la position initiale à l'ouverture, puis écoute scroll/resize
  useEffect(() => {
    if (!open) return;
    const frameId = window.requestAnimationFrame(update);
    window.addEventListener("scroll", update, true);
    window.addEventListener("resize", update);
    return () => {
      window.cancelAnimationFrame(frameId);
      window.removeEventListener("scroll", update, true);
      window.removeEventListener("resize", update);
    };
  }, [open, update]);

  return { style, update };
}
