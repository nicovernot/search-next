"use client";

import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { api } from "../lib/api";
import { STORAGE_KEYS } from "../lib/storage-keys";

interface AuthUser {
  id: number;
  email: string;
}

interface AuthContextValue {
  user: AuthUser | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
  loading: boolean;
  error: string | null;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

function isErrorWithMessage(error: unknown): error is Error {
  return error instanceof Error;
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const storedToken = localStorage.getItem(STORAGE_KEYS.TOKEN);
    const storedUser = localStorage.getItem(STORAGE_KEYS.USER);
    if (storedToken && storedUser) {
      try {
        setToken(storedToken);
        setUser(JSON.parse(storedUser));
      } catch {
        localStorage.removeItem(STORAGE_KEYS.TOKEN);
        localStorage.removeItem(STORAGE_KEYS.USER);
      }
    }
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.login(email, password);
      if (!res.ok) throw new Error("auth_error");

      const data = await res.json();
      const accessToken: string = data.access_token;
      const payloadBase64 = accessToken.split(".")[1];
      const payload = JSON.parse(atob(payloadBase64));
      const authUser: AuthUser = { id: Number(payload.sub), email };

      setToken(accessToken);
      setUser(authUser);
      localStorage.setItem(STORAGE_KEYS.TOKEN, accessToken);
      localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(authUser));
    } catch (err: unknown) {
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
        const res = await api.register(email, password);
        if (!res.ok) {
          throw new Error(res.status === 409 ? "email_exists" : "register_error");
        }
        await login(email, password);
      } catch (err: unknown) {
        if (!isErrorWithMessage(err) || err.message !== "auth_error") {
          setError(isErrorWithMessage(err) ? err.message : "register_error");
        }
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
    localStorage.removeItem(STORAGE_KEYS.TOKEN);
    localStorage.removeItem(STORAGE_KEYS.USER);
  }, []);

  const clearError = useCallback(() => setError(null), []);

  return (
    <AuthContext.Provider
      value={{ user, token, login, register, logout, loading, error, clearError }}
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
