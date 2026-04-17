"use client";

import { useTranslations } from "next-intl";
import { LogIn, UserPlus } from "lucide-react";

interface AuthButtonsProps {
  onLogin: () => void;
  onRegister: () => void;
}

/** Boutons Connexion / S'inscrire affichés dans le header. */
export default function AuthButtons({ onLogin, onRegister }: AuthButtonsProps) {
  const t = useTranslations();

  return (
    <div className="flex items-center gap-2" data-testid="auth-buttons">
      <button
        data-testid="btn-open-login"
        onClick={onLogin}
        className="flex items-center gap-2 px-4 py-2 text-sm font-bold text-foreground bg-secondary border border-border rounded-xl hover:bg-muted hover:border-highlight/40 transition-all"
      >
        <LogIn size={15} />
        {t("login")}
      </button>
      <button
        data-testid="btn-open-register"
        onClick={onRegister}
        className="flex items-center gap-2 px-4 py-2 text-sm font-bold text-white bg-highlight rounded-xl hover:brightness-110 transition-all premium-shadow"
      >
        <UserPlus size={15} />
        {t("register")}
      </button>
    </div>
  );
}
