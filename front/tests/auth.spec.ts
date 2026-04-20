/**
 * Tests E2E — Authentification (Inscription / Connexion / Déconnexion)
 *
 * Prérequis : backend FastAPI + PostgreSQL opérationnels
 * Lancer avec : BASE_URL=http://localhost:3003 npx playwright test auth.spec.ts
 */

import { test, expect, Page } from "@playwright/test";

// Helpers ----------------------------------------------------------------

/** Génère un email unique pour éviter les conflits entre runs */
const uniqueEmail = () => `test_${Date.now()}_${Math.random().toString(36).slice(2)}@example.com`;

/** Ouvre la page et attend que le header soit visible */
async function gotoHome(page: Page) {
  await page.goto("/fr/");
  await expect(page.locator("header")).toBeVisible({ timeout: 15000 });
}

/** S'inscrit avec les identifiants fournis et attend la fermeture de la modal */
async function registerUser(page: Page, email: string, password: string) {
  await page.getByTestId("btn-open-register").click();
  await expect(page.getByTestId("auth-modal")).toBeVisible();

  await page.getByTestId("input-email").fill(email);
  await page.getByTestId("input-password").fill(password);
  await page.getByTestId("input-confirm-password").fill(password);
  await page.getByTestId("btn-auth-submit").click();

  // Modal se ferme en cas de succès
  await expect(page.getByTestId("auth-modal")).not.toBeVisible({ timeout: 10000 });
}

/** Se connecte avec les identifiants fournis */
async function loginUser(page: Page, email: string, password: string) {
  await page.getByTestId("btn-open-login").click();
  await expect(page.getByTestId("auth-modal")).toBeVisible();

  await page.getByTestId("tab-login").click();
  await page.getByTestId("input-email").fill(email);
  await page.getByTestId("input-password").fill(password);
  await page.getByTestId("btn-auth-submit").click();

  await expect(page.getByTestId("auth-modal")).not.toBeVisible({ timeout: 10000 });
}

// Tests ------------------------------------------------------------------

test.describe("Header — boutons d'authentification", () => {
  test("affiche deux boutons distincts Connexion et S'inscrire", async ({ page }) => {
    await gotoHome(page);

    const loginBtn = page.getByTestId("btn-open-login");
    const registerBtn = page.getByTestId("btn-open-register");

    await expect(loginBtn).toBeVisible();
    await expect(registerBtn).toBeVisible();

    // Le bouton S'inscrire doit être visuellement distinct (couleur highlight)
    await expect(registerBtn).toHaveClass(/bg-highlight/);
  });
});

test.describe("Modal d'authentification", () => {
  test("s'ouvre sur l'onglet Connexion au clic sur Connexion", async ({ page }) => {
    await gotoHome(page);
    await page.getByTestId("btn-open-login").click();

    await expect(page.getByTestId("auth-modal")).toBeVisible();
    await expect(page.getByTestId("tab-login")).toHaveClass(/bg-highlight/);
    await expect(page.getByTestId("tab-register")).not.toHaveClass(/bg-highlight/);
  });

  test("s'ouvre sur l'onglet S'inscrire au clic sur S'inscrire", async ({ page }) => {
    await gotoHome(page);
    await page.getByTestId("btn-open-register").click();

    await expect(page.getByTestId("auth-modal")).toBeVisible();
    await expect(page.getByTestId("tab-register")).toHaveClass(/bg-highlight/);
    // Champ confirmation visible uniquement sur l'onglet Register
    await expect(page.getByTestId("input-confirm-password")).toBeVisible();
  });

  test("se ferme au clic sur le bouton de fermeture", async ({ page }) => {
    await gotoHome(page);
    await page.getByTestId("btn-open-login").click();
    await page.getByTestId("auth-modal-close").click();
    await expect(page.getByTestId("auth-modal")).not.toBeVisible();
  });

  test("se ferme au clic sur le backdrop", async ({ page }) => {
    await gotoHome(page);
    await page.getByTestId("btn-open-login").click();
    // Clic sur le backdrop (coordonnées hors de la card)
    await page.mouse.click(10, 10);
    await expect(page.getByTestId("auth-modal")).not.toBeVisible();
  });

  test("le champ confirmation est absent sur l'onglet Connexion", async ({ page }) => {
    await gotoHome(page);
    await page.getByTestId("btn-open-login").click();
    await expect(page.getByTestId("input-confirm-password")).not.toBeVisible();
  });

  test("bascule vers S'inscrire via le lien intérieur", async ({ page }) => {
    await gotoHome(page);
    await page.getByTestId("btn-open-login").click();
    // Le lien "Pas encore de compte ?" switche l'onglet
    await page.getByTestId("btn-switch-to-register").click();
    await expect(page.getByTestId("tab-register")).toHaveClass(/bg-highlight/);
  });
});

test.describe("Inscription", () => {
  test("inscription réussie — modal fermée et bouton Mes Recherches visible", async ({ page }) => {
    await gotoHome(page);
    const email = uniqueEmail();
    await registerUser(page, email, "password123");

    // Après inscription auto-login : on voit le panneau saved searches
    await expect(page.getByTestId("btn-saved-searches")).toBeVisible();
    await expect(page.getByTestId("btn-logout")).toBeVisible();
    // Les boutons login/register disparaissent
    await expect(page.getByTestId("btn-open-login")).not.toBeVisible();
  });

  test("inscription échoue si les mots de passe ne correspondent pas", async ({ page }) => {
    await gotoHome(page);
    await page.getByTestId("btn-open-register").click();

    await page.getByTestId("input-email").fill(uniqueEmail());
    await page.getByTestId("input-password").fill("password123");
    await page.getByTestId("input-confirm-password").fill("different456");
    await page.getByTestId("btn-auth-submit").click();

    // Message d'erreur visible, modal reste ouverte
    await expect(page.getByTestId("auth-error")).toBeVisible();
    await expect(page.getByTestId("auth-modal")).toBeVisible();
  });

  test("inscription échoue si l'email est déjà utilisé", async ({ page }) => {
    await gotoHome(page);
    const email = uniqueEmail();

    // Premier compte
    await registerUser(page, email, "password123");
    await page.getByTestId("btn-logout").click();

    // Deuxième tentative avec le même email
    await page.getByTestId("btn-open-register").click();
    await page.getByTestId("input-email").fill(email);
    await page.getByTestId("input-password").fill("password123");
    await page.getByTestId("input-confirm-password").fill("password123");
    await page.getByTestId("btn-auth-submit").click();

    await expect(page.getByTestId("auth-error")).toBeVisible();
  });
});

test.describe("Connexion", () => {
  test("connexion réussie avec un compte existant", async ({ page }) => {
    await gotoHome(page);
    const email = uniqueEmail();

    // Créer le compte d'abord
    await registerUser(page, email, "password123");
    await page.getByTestId("btn-logout").click();

    // Se reconnecter
    await loginUser(page, email, "password123");

    await expect(page.getByTestId("btn-saved-searches")).toBeVisible();
    await expect(page.getByTestId("btn-logout")).toBeVisible();
  });

  test("connexion échoue avec un mauvais mot de passe", async ({ page }) => {
    await gotoHome(page);
    const email = uniqueEmail();

    // Créer le compte
    await registerUser(page, email, "correctpassword");
    await page.getByTestId("btn-logout").click();

    // Tentative avec mauvais mdp
    await page.getByTestId("btn-open-login").click();
    await page.getByTestId("input-email").fill(email);
    await page.getByTestId("input-password").fill("wrongpassword");
    await page.getByTestId("btn-auth-submit").click();

    await expect(page.getByTestId("auth-error")).toBeVisible();
    await expect(page.getByTestId("auth-modal")).toBeVisible();
  });

  test("connexion échoue avec un email inexistant", async ({ page }) => {
    await gotoHome(page);
    await page.getByTestId("btn-open-login").click();
    await page.getByTestId("input-email").fill("nonexistent@example.com");
    await page.getByTestId("input-password").fill("password123");
    await page.getByTestId("btn-auth-submit").click();

    await expect(page.getByTestId("auth-error")).toBeVisible();
  });
});

test.describe("Déconnexion", () => {
  test("déconnexion restaure les boutons Connexion et S'inscrire", async ({ page }) => {
    await gotoHome(page);
    await registerUser(page, uniqueEmail(), "password123");

    await page.getByTestId("btn-logout").click();

    await expect(page.getByTestId("btn-open-login")).toBeVisible();
    await expect(page.getByTestId("btn-open-register")).toBeVisible();
    await expect(page.getByTestId("btn-saved-searches")).not.toBeVisible();
  });

  test("la session persiste après rechargement de page", async ({ page }) => {
    await gotoHome(page);
    await registerUser(page, uniqueEmail(), "password123");

    // Recharger
    await page.reload();
    await expect(page.locator("header")).toBeVisible({ timeout: 15000 });

    // L'utilisateur est toujours connecté (localStorage)
    await expect(page.getByTestId("btn-saved-searches")).toBeVisible();
  });
});
