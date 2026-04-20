"use client";

import React, { useState } from "react";
import { useTranslations } from "next-intl";
import { Building2 } from "lucide-react";

interface LdapLoginFormProps {
  loading: boolean;
  onSubmit: (username: string, password: string) => Promise<void>;
}

export function LdapLoginForm({ loading, onSubmit }: LdapLoginFormProps) {
  const t = useTranslations();
  const [showLdap, setShowLdap] = useState(false);
  const [ldapUsername, setLdapUsername] = useState("");
  const [ldapPassword, setLdapPassword] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSubmit(ldapUsername, ldapPassword);
  };

  return (
    <div className="mt-2">
      <button
        type="button"
        data-testid="btn-toggle-ldap"
        onClick={() => setShowLdap((visible) => !visible)}
        className="flex items-center justify-center gap-2 w-full py-3 rounded-xl border border-border text-sm font-bold text-foreground hover:bg-muted hover:border-highlight/40 transition-all"
      >
        <Building2 size={15} />
        {t("ldapLoginButton")}
      </button>

      {showLdap && (
        <form onSubmit={handleSubmit} className="mt-3 space-y-3" data-testid="ldap-form">
          <input
            data-testid="input-ldap-username"
            type="text"
            value={ldapUsername}
            onChange={(e) => setLdapUsername(e.target.value)}
            required
            autoComplete="username"
            placeholder={t("ldapUsername")}
            className="w-full px-4 py-3 rounded-xl border border-border text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:border-highlight focus:ring-2 focus:ring-highlight/20 transition-all text-sm"
            style={{ backgroundColor: "hsl(var(--background))" }}
          />
          <input
            data-testid="input-ldap-password"
            type="password"
            value={ldapPassword}
            onChange={(e) => setLdapPassword(e.target.value)}
            required
            autoComplete="current-password"
            placeholder={t("ldapPassword")}
            className="w-full px-4 py-3 rounded-xl border border-border text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:border-highlight focus:ring-2 focus:ring-highlight/20 transition-all text-sm"
            style={{ backgroundColor: "hsl(var(--background))" }}
          />
          <button
            data-testid="btn-ldap-submit"
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-highlight text-white rounded-xl font-bold text-sm hover:brightness-110 active:scale-95 transition-all premium-shadow disabled:opacity-60"
          >
            {loading ? (
              <div className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin mx-auto" />
            ) : t("ldapLoginTitle")}
          </button>
        </form>
      )}
    </div>
  );
}
