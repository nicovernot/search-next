/**
 * Tests E2E — Authentification LDAP et SSO (spec 011)
 *
 * Prérequis : backend FastAPI + PostgreSQL opérationnels, NEXT_PUBLIC_LDAP_ENABLED=true dans front/.env
 *
 * Couverture :
 *   - Rendu UI LDAP (section conditionnelle, toggle formulaire)
 *   - Erreur LDAP quand le backend LDAP n'est pas configuré (LDAP_ENABLED=false → 503)
 *   - Callback SSO (?sso_error= et ?auth_token= dans l'URL)
 *   - Coexistence : un compte local reste accessible quand LDAP est activé en UI
 *
 * Tests nécessitant un vrai serveur LDAP / OIDC sont annotés test.skip.
 *
 * Lancer avec : BASE_URL=http://localhost:3000 npx playwright test auth-ldap-sso.spec.ts
 */

import { test, expect, Page } from "@playwright/test";

// ── Helpers ────────────────────────────────────────────────────────────────

const uniqueEmail = () =>
  `test_${Date.now()}_${Math.random().toString(36).slice(2)}@example.com`;

async function gotoHome(page: Page) {
  await page.goto("/fr/");
  await expect(page.locator("header")).toBeVisible({ timeout: 15000 });
}

async function openLoginModal(page: Page) {
  await page.getByTestId("btn-open-login").click();
  await expect(page.getByTestId("auth-modal")).toBeVisible();
  // S'assurer d'être sur l'onglet Connexion
  await page.getByTestId("tab-login").click();
}

async function registerUser(page: Page, email: string, password: string) {
  await page.getByTestId("btn-open-register").click();
  await expect(page.getByTestId("auth-modal")).toBeVisible();
  await page.getByTestId("input-email").fill(email);
  await page.getByTestId("input-password").fill(password);
  await page.getByTestId("input-confirm-password").fill(password);
  await page.getByTestId("btn-auth-submit").click();
  await expect(page.getByTestId("auth-modal")).not.toBeVisible({ timeout: 10000 });
}

/**
 * Construit un JWT minimal décodable côté client (sans validation de signature).
 * Utilisé uniquement pour tester le handler de callback SSO — non valide côté serveur.
 */
function buildFakeJwt(payload: Record<string, unknown>): string {
  const header = btoa(JSON.stringify({ alg: "HS256", typ: "JWT" }))
    .replace(/\+/g, "-").replace(/\//g, "_").replace(/=/g, "");
  const body = btoa(JSON.stringify(payload))
    .replace(/\+/g, "-").replace(/\//g, "_").replace(/=/g, "");
  return `${header}.${body}.fakesignature`;
}

// ── Section LDAP — rendu conditionnel ──────────────────────────────────────

test.describe("Authentification LDAP — rendu UI", () => {
  // Ces tests supposent NEXT_PUBLIC_LDAP_ENABLED=true (valeur de front/.env)

  test("le bouton LDAP est visible dans la modal onglet Connexion", async ({ page }) => {
    await gotoHome(page);
    await openLoginModal(page);

    await expect(page.getByTestId("btn-toggle-ldap")).toBeVisible();
  });

  test("le formulaire LDAP apparaît au clic sur le bouton LDAP", async ({ page }) => {
    await gotoHome(page);
    await openLoginModal(page);

    // Par défaut le formulaire est masqué
    await expect(page.getByTestId("ldap-form")).not.toBeVisible();

    await page.getByTestId("btn-toggle-ldap").click();
    await expect(page.getByTestId("ldap-form")).toBeVisible();
  });

  test("le formulaire LDAP se referme au second clic (toggle)", async ({ page }) => {
    await gotoHome(page);
    await openLoginModal(page);

    await page.getByTestId("btn-toggle-ldap").click();
    await expect(page.getByTestId("ldap-form")).toBeVisible();

    await page.getByTestId("btn-toggle-ldap").click();
    await expect(page.getByTestId("ldap-form")).not.toBeVisible();
  });

  test("les champs identifiant et mot de passe LDAP sont présents", async ({ page }) => {
    await gotoHome(page);
    await openLoginModal(page);
    await page.getByTestId("btn-toggle-ldap").click();

    await expect(page.getByTestId("input-ldap-username")).toBeVisible();
    await expect(page.getByTestId("input-ldap-password")).toBeVisible();
    await expect(page.getByTestId("btn-ldap-submit")).toBeVisible();
  });

  test("le bouton LDAP est absent sur l'onglet S'inscrire", async ({ page }) => {
    await gotoHome(page);
    await page.getByTestId("btn-open-register").click();
    await expect(page.getByTestId("auth-modal")).toBeVisible();

    // Section SSO/LDAP n'est rendue que sur l'onglet login
    await expect(page.getByTestId("btn-toggle-ldap")).not.toBeVisible();
  });
});

// ── Authentification LDAP — comportement backend ───────────────────────────

test.describe("Authentification LDAP — erreurs", () => {
  test("affiche une erreur si le backend LDAP n'est pas activé ou les identifiants sont incorrects", async ({ page }) => {
    // Quand LDAP_ENABLED=false côté backend → HTTP 503 → "ldap_error" affiché
    // Quand LDAP_ENABLED=true mais identifiants invalides → HTTP 401 → "ldap_error" affiché
    await gotoHome(page);
    await openLoginModal(page);
    await page.getByTestId("btn-toggle-ldap").click();

    await page.getByTestId("input-ldap-username").fill("jdupont");
    await page.getByTestId("input-ldap-password").fill("wrongpassword");
    await page.getByTestId("btn-ldap-submit").click();

    await expect(page.getByTestId("auth-error")).toBeVisible({ timeout: 10000 });
    // La modal reste ouverte
    await expect(page.getByTestId("auth-modal")).toBeVisible();
  });

  test("les champs LDAP sont requis — soumission vide ne déclenche pas de requête", async ({ page }) => {
    await gotoHome(page);
    await openLoginModal(page);
    await page.getByTestId("btn-toggle-ldap").click();

    // Soumettre sans remplir → validation HTML native, pas de requête réseau
    await page.getByTestId("btn-ldap-submit").click();
    await expect(page.getByTestId("auth-modal")).toBeVisible();
    await expect(page.getByTestId("auth-error")).not.toBeVisible();
  });

  test.skip("identifiants LDAP valides → session ouverte (nécessite un serveur LDAP de test)", async ({ page }) => {
    // Ce test requiert LDAP_ENABLED=true et un annuaire LDAP accessible
    await gotoHome(page);
    await openLoginModal(page);
    await page.getByTestId("btn-toggle-ldap").click();

    await page.getByTestId("input-ldap-username").fill(process.env.TEST_LDAP_USERNAME ?? "");
    await page.getByTestId("input-ldap-password").fill(process.env.TEST_LDAP_PASSWORD ?? "");
    await page.getByTestId("btn-ldap-submit").click();

    await expect(page.getByTestId("auth-modal")).not.toBeVisible({ timeout: 10000 });
    await expect(page.getByTestId("btn-saved-searches")).toBeVisible();
    await expect(page.getByTestId("btn-logout")).toBeVisible();
  });
});

// ── Callback SSO — traitement de l'URL de retour ───────────────────────────

test.describe("Callback SSO — traitement URL", () => {
  test("?sso_error= dans l'URL est retiré et l'erreur s'affiche à l'ouverture de la modal", async ({ page }) => {
    // Simule le retour d'un IdP avec une erreur
    await page.goto("/fr/?sso_error=oidc_invalid_state");
    await expect(page.locator("header")).toBeVisible({ timeout: 15000 });

    // Le paramètre sso_error doit être supprimé de l'URL immédiatement
    await expect(page).not.toHaveURL(/sso_error/);

    // L'erreur est dans l'état AuthContext — visible en ouvrant la modal
    await page.getByTestId("btn-open-login").click();
    await expect(page.getByTestId("auth-error")).toBeVisible({ timeout: 5000 });
  });

  test("?auth_token= valide dans l'URL crée une session et est retiré de l'URL", async ({ page }) => {
    // JWT fake mais parseable côté client (sub + email présents)
    const fakeJwt = buildFakeJwt({ sub: "99999", email: "sso-callback@example.com", exp: 9999999999 });

    await page.goto(`/fr/?auth_token=${fakeJwt}`);
    await expect(page.locator("header")).toBeVisible({ timeout: 15000 });

    // Paramètre retiré de l'URL
    await expect(page).not.toHaveURL(/auth_token/);

    // Session active : boutons post-login visibles
    await expect(page.getByTestId("btn-saved-searches")).toBeVisible({ timeout: 5000 });
    await expect(page.getByTestId("btn-logout")).toBeVisible();

    // Nettoyage
    await page.getByTestId("btn-logout").click();
  });

  test("?auth_token= invalide (non décodable) n'ouvre pas de session", async ({ page }) => {
    await page.goto("/fr/?auth_token=not.a.valid.jwt");
    await expect(page.locator("header")).toBeVisible({ timeout: 15000 });

    // Paramètre retiré de l'URL
    await expect(page).not.toHaveURL(/auth_token/);

    // Pas de session — boutons login/register visibles
    await expect(page.getByTestId("btn-open-login")).toBeVisible({ timeout: 5000 });
    await expect(page.getByTestId("btn-open-register")).toBeVisible();
  });

  test.skip("flux SSO complet (nécessite un IdP OIDC de test)", async ({ page }) => {
    // Ce test requiert SSO_OIDC_ENABLED=true + NEXT_PUBLIC_SSO_ENABLED=true + IdP accessible
    await gotoHome(page);
    await openLoginModal(page);
    // Le bouton SSO n'est visible que si NEXT_PUBLIC_SSO_ENABLED=true
    await expect(page.getByTestId("btn-sso-login")).toBeVisible();
    // Clic → redirection vers l'IdP (hors scope du test E2E sans mock IdP)
  });
});

// ── Coexistence local + LDAP ───────────────────────────────────────────────

test.describe("Coexistence — compte local et LDAP activé en UI", () => {
  test("un compte local peut toujours se connecter par email/password quand LDAP est disponible", async ({ page }) => {
    await gotoHome(page);
    const email = uniqueEmail();
    const password = "password123";

    // Créer un compte local
    await registerUser(page, email, password);
    await page.getByTestId("btn-logout").click();

    // Se reconnecter en local (pas via LDAP)
    await page.getByTestId("btn-open-login").click();
    await page.getByTestId("tab-login").click();
    await page.getByTestId("input-email").fill(email);
    await page.getByTestId("input-password").fill(password);
    await page.getByTestId("btn-auth-submit").click();

    await expect(page.getByTestId("auth-modal")).not.toBeVisible({ timeout: 10000 });
    await expect(page.getByTestId("btn-saved-searches")).toBeVisible();
  });

  test("un compte local avec email existant ne peut pas se connecter via le formulaire LDAP", async ({ page }) => {
    // Si LDAP_ENABLED=false côté backend → HTTP 503/401 → erreur affichée de toute façon
    // Ce test vérifie que la section LDAP visible en UI n'interfère pas avec le flux local
    await gotoHome(page);
    const email = uniqueEmail();
    await registerUser(page, email, "password123");
    await page.getByTestId("btn-logout").click();

    // Tenter LDAP avec l'email d'un compte local (backend LDAP désactivé → erreur)
    await openLoginModal(page);
    await page.getByTestId("btn-toggle-ldap").click();
    await page.getByTestId("input-ldap-username").fill(email);
    await page.getByTestId("input-ldap-password").fill("password123");
    await page.getByTestId("btn-ldap-submit").click();

    await expect(page.getByTestId("auth-error")).toBeVisible({ timeout: 10000 });
    // Le compte local existe toujours et est intact
    await page.getByTestId("auth-modal-close").click();

    await page.getByTestId("btn-open-login").click();
    await page.getByTestId("input-email").fill(email);
    await page.getByTestId("input-password").fill("password123");
    await page.getByTestId("btn-auth-submit").click();
    await expect(page.getByTestId("auth-modal")).not.toBeVisible({ timeout: 10000 });
    await expect(page.getByTestId("btn-saved-searches")).toBeVisible();
  });
});
