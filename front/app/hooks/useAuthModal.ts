/**
 * Gère l'état ouvert/fermé et l'onglet actif de la modal d'authentification.
 * Intention : isoler l'état UI de la modal hors de AuthContext (qui ne doit gérer que l'authentification).
 * Résultat : retourne open/tab/openModal/closeModal à passer en props à AuthModal et AuthButtons.
 */
import { useState, useCallback } from "react";

export type ModalTab = "login" | "register";

export function useAuthModal() {
  const [open, setOpen] = useState(false);
  const [tab, setTab] = useState<ModalTab>("login");

  const openModal = useCallback((nextTab: ModalTab = "login") => {
    setTab(nextTab);
    setOpen(true);
  }, []);

  const closeModal = useCallback(() => setOpen(false), []);

  return { open, tab, openModal, closeModal };
}
