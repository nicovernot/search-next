"use client";

import { useState, useEffect, useCallback } from "react";
import { createPortal } from "react-dom";
import { useTranslations } from "next-intl";
import { useAuth } from "../context/AuthContext";
import { X, LogIn, UserPlus, Eye, EyeOff } from "lucide-react";

/**
 * Modal login/register rendue via createPortal sur document.body.
 * Cela échappe à tout stacking context (header z-10, search z-30, etc.)
 * et garantit que z-[9999] est relatif au root stacking context.
 */
export default function AuthModal() {
  const t = useTranslations();
  const { login, register, loading, error, clearError, modalOpen, modalTab, closeModal } =
    useAuth();

  const [tab, setTab] = useState<"login" | "register">(modalTab);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [showPwd, setShowPwd] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);
  const handleClose = useCallback(() => {
    clearError();
    closeModal();
  }, [clearError, closeModal]);

  // Synchronise l'onglet quand le contexte change
  useEffect(() => { setTab(modalTab); }, [modalTab]);

  // Réinitialise le formulaire à la fermeture
  useEffect(() => {
    if (!modalOpen) {
      setEmail("");
      setPassword("");
      setConfirm("");
      setLocalError(null);
      setShowPwd(false);
    }
  }, [modalOpen]);

  // Fermer au clavier Échap
  useEffect(() => {
    if (!modalOpen) return;
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") handleClose(); };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [modalOpen, handleClose]);

  const switchTab = (next: "login" | "register") => {
    setTab(next);
    setLocalError(null);
    clearError();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError(null);

    if (tab === "register" && password !== confirm) {
      setLocalError(t("passwordMismatch"));
      return;
    }

    try {
      if (tab === "login") {
        await login(email, password);
      } else {
        await register(email, password);
      }
      handleClose();
    } catch {
      // error déjà dans AuthContext
    }
  };

  const displayError =
    localError ||
    (error === "auth_error"
      ? t("authError")
      : error === "email_exists"
      ? t("emailAlreadyExists")
      : error === "register_error"
      ? t("registerError")
      : null);

  if (typeof document === "undefined" || !modalOpen) return null;

  return createPortal(
    // Container : fixed inset-0, z-[9999] relatif au ROOT stacking context
    // car rendu directement sur document.body via portal
    <div
      className="fixed inset-0 flex items-center justify-center p-4"
      style={{ zIndex: 9999 }}
      onClick={handleClose}
      data-testid="auth-modal"
    >
      {/* Backdrop purement visuel — pointer-events-none */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        style={{ pointerEvents: "none" }}
      />

      {/* Card : stopPropagation pour ne pas fermer au clic intérieur */}
      <div
        className="relative w-full max-w-md rounded-3xl overflow-hidden shadow-2xl max-h-[90vh] overflow-y-auto"
        style={{ zIndex: 1 }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Gradient top bar */}
        <div className="h-1.5 w-full bg-gradient-to-r from-highlight via-primary to-highlight" />

        {/* Card body */}
        <div
          className="border border-border border-t-0 rounded-b-3xl p-8"
          style={{ backgroundColor: "hsl(var(--card))" }}
        >
          {/* Header */}
          <div className="flex items-start justify-between mb-6">
            <div>
              <h2 className="text-2xl font-extrabold text-foreground font-serif tracking-tight">
                {tab === "login" ? t("loginTitle") : t("registerTitle")}
              </h2>
              <p className="text-sm text-muted-foreground mt-1">
                {tab === "login" ? t("loginSubtitle") : t("registerSubtitle")}
              </p>
            </div>
            <button
              data-testid="auth-modal-close"
              type="button"
              onClick={handleClose}
              className="w-8 h-8 shrink-0 flex items-center justify-center rounded-full text-muted-foreground hover:bg-muted hover:text-foreground transition-all"
            >
              <X size={18} />
            </button>
          </div>

          {/* Tab switcher */}
          <div
            className="flex gap-1 p-1 rounded-xl mb-6"
            style={{ backgroundColor: "hsl(var(--secondary))" }}
            data-testid="auth-tabs"
          >
            {(["login", "register"] as const).map((t_) => (
              <button
                key={t_}
                data-testid={`tab-${t_}`}
                type="button"
                onClick={() => switchTab(t_)}
                className={`flex-1 flex items-center justify-center gap-2 py-2.5 text-sm font-bold rounded-lg transition-all ${
                  tab === t_
                    ? "bg-highlight text-white shadow-md"
                    : "text-muted-foreground hover:text-foreground hover:bg-muted"
                }`}
              >
                {t_ === "login" ? <LogIn size={14} /> : <UserPlus size={14} />}
                {t_ === "login" ? t("loginTitle") : t("registerTitle")}
              </button>
            ))}
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4" data-testid="auth-form">
            {/* Email */}
            <div>
              <label className="block text-xs font-bold text-muted-foreground uppercase tracking-widest mb-2">
                {t("email")}
              </label>
              <input
                data-testid="input-email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoComplete="email"
                placeholder="you@example.com"
                className="w-full px-4 py-3 rounded-xl border border-border text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:border-highlight focus:ring-2 focus:ring-highlight/20 transition-all text-sm"
                style={{ backgroundColor: "hsl(var(--background))" }}
              />
            </div>

            {/* Password */}
            <div>
              <label className="block text-xs font-bold text-muted-foreground uppercase tracking-widest mb-2">
                {t("password")}
              </label>
              <div className="relative">
                <input
                  data-testid="input-password"
                  type={showPwd ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  autoComplete={tab === "login" ? "current-password" : "new-password"}
                  placeholder="••••••••"
                  className="w-full px-4 py-3 pr-11 rounded-xl border border-border text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:border-highlight focus:ring-2 focus:ring-highlight/20 transition-all text-sm"
                  style={{ backgroundColor: "hsl(var(--background))" }}
                />
                <button
                  type="button"
                  onClick={() => setShowPwd(!showPwd)}
                  tabIndex={-1}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                >
                  {showPwd ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            {/* Confirm password — register only */}
            {tab === "register" && (
              <div>
                <label className="block text-xs font-bold text-muted-foreground uppercase tracking-widest mb-2">
                  {t("confirmPassword")}
                </label>
                <input
                  data-testid="input-confirm-password"
                  type={showPwd ? "text" : "password"}
                  value={confirm}
                  onChange={(e) => setConfirm(e.target.value)}
                  required
                  autoComplete="new-password"
                  placeholder="••••••••"
                  className="w-full px-4 py-3 rounded-xl border border-border text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:border-highlight focus:ring-2 focus:ring-highlight/20 transition-all text-sm"
                  style={{ backgroundColor: "hsl(var(--background))" }}
                />
              </div>
            )}

            {/* Error */}
            {displayError && (
              <div
                data-testid="auth-error"
                className="flex items-start gap-2.5 p-3.5 rounded-xl text-sm border"
                style={{
                  backgroundColor: "hsl(0 84.2% 60.2% / 0.08)",
                  borderColor: "hsl(0 84.2% 60.2% / 0.25)",
                  color: "hsl(0 72% 42%)",
                }}
              >
                <span className="shrink-0 mt-0.5">⚠</span>
                {displayError}
              </div>
            )}

            {/* Submit */}
            <button
              data-testid="btn-auth-submit"
              type="submit"
              disabled={loading}
              className="w-full py-3.5 bg-highlight text-white rounded-xl font-bold text-sm hover:brightness-110 active:scale-95 transition-all premium-shadow disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2 mt-1"
            >
              {loading ? (
                <div className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
              ) : tab === "login" ? (
                <><LogIn size={15} /> {t("loginTitle")}</>
              ) : (
                <><UserPlus size={15} /> {t("registerTitle")}</>
              )}
            </button>

            {/* Switch tab link */}
            <p className="text-center text-xs text-muted-foreground pt-1">
              {tab === "login" ? (
                <>
                  {t("noAccount")}{" "}
                  <button
                    data-testid="btn-switch-to-register"
                    type="button"
                    onClick={() => switchTab("register")}
                    className="text-highlight font-bold hover:underline"
                  >
                    {t("registerTitle")}
                  </button>
                </>
              ) : (
                <>
                  {t("alreadyAccount")}{" "}
                  <button
                    data-testid="btn-switch-to-login"
                    type="button"
                    onClick={() => switchTab("login")}
                    className="text-highlight font-bold hover:underline"
                  >
                    {t("loginTitle")}
                  </button>
                </>
              )}
            </p>
          </form>
        </div>
      </div>
    </div>,
    document.body
  );
}
