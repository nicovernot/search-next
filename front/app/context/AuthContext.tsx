"use client";

import React, { createContext, useContext, useState, useEffect, useCallback } from "react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8007";

interface AuthUser {
  id: number;
  email: string;
}

type ModalTab = "login" | "register";

interface AuthContextValue {
  user: AuthUser | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
  loading: boolean;
  error: string | null;
  clearError: () => void;
  // Modal state (géré ici pour que le portal puisse être hors du header)
  modalOpen: boolean;
  modalTab: ModalTab;
  openModal: (tab?: ModalTab) => void;
  closeModal: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [modalTab, setModalTab] = useState<ModalTab>("login");

  useEffect(() => {
    const storedToken = localStorage.getItem("auth_token");
    const storedUser = localStorage.getItem("auth_user");
    if (storedToken && storedUser) {
      try {
        setToken(storedToken);
        setUser(JSON.parse(storedUser));
      } catch {
        localStorage.removeItem("auth_token");
        localStorage.removeItem("auth_user");
      }
    }
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      if (!res.ok) throw new Error("auth_error");

      const data = await res.json();
      const accessToken: string = data.access_token;
      const payloadBase64 = accessToken.split(".")[1];
      const payload = JSON.parse(atob(payloadBase64));
      const authUser: AuthUser = { id: Number(payload.sub), email };

      setToken(accessToken);
      setUser(authUser);
      localStorage.setItem("auth_token", accessToken);
      localStorage.setItem("auth_user", JSON.stringify(authUser));
    } catch (err: any) {
      setError("auth_error");
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const register = useCallback(
    async (email: string, password: string) => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`${API_BASE_URL}/auth/register`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        });
        if (!res.ok) throw new Error("register_error");
        await login(email, password);
      } catch (err: any) {
        if (err.message !== "auth_error") setError("register_error");
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [login]
  );

  const logout = useCallback(() => {
    setUser(null);
    setToken(null);
    localStorage.removeItem("auth_token");
    localStorage.removeItem("auth_user");
  }, []);

  const clearError = useCallback(() => setError(null), []);

  const openModal = useCallback((tab: ModalTab = "login") => {
    setModalTab(tab);
    setModalOpen(true);
    setError(null);
  }, []);

  const closeModal = useCallback(() => {
    setModalOpen(false);
    setError(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user, token, login, register, logout,
        loading, error, clearError,
        modalOpen, modalTab, openModal, closeModal,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
