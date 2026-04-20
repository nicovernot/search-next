/**
 * Tests E2E — Sauvegarde de Recherches
 *
 * Prérequis : backend FastAPI + PostgreSQL opérationnels
 * Lancer avec : BASE_URL=http://localhost:3003 npx playwright test saved-searches.spec.ts
 */

import { test, expect, Page } from "@playwright/test";

// Helpers ----------------------------------------------------------------

const uniqueEmail = () =>
  `saved_${Date.now()}_${Math.random().toString(36).slice(2)}@example.com`;

async function gotoHome(page: Page) {
  await page.goto("/fr/");
  await expect(page.locator("header")).toBeVisible({ timeout: 15000 });
}

async function registerAndLogin(page: Page, email: string, password: string) {
  await page.getByTestId("btn-open-register").click();
  await expect(page.getByTestId("auth-modal")).toBeVisible();
  await page.getByTestId("input-email").fill(email);
  await page.getByTestId("input-password").fill(password);
  await page.getByTestId("input-confirm-password").fill(password);
  await page.getByTestId("btn-auth-submit").click();
  await expect(page.getByTestId("auth-modal")).not.toBeVisible({ timeout: 10000 });
  await expect(page.getByTestId("btn-saved-searches")).toBeVisible();
}

async function doSearch(page: Page, query: string) {
  const searchInput = page.getByPlaceholder(/Rechercher|Search/i).first();
  await searchInput.fill(query);
  await searchInput.press("Enter");
  // Attendre que les résultats ou le spinner apparaissent
  await page.waitForTimeout(1000);
}

async function waitForResults(page: Page, timeout = 15000) {
  // Wait for the results list to contain at least one result item
  await expect(page.locator('[data-testid="results-list"] [data-testid="result-item"]').first())
    .toBeVisible({ timeout });
}

async function openSavedSearchesPanel(page: Page) {
  await page.getByTestId("btn-saved-searches").click();
  await expect(page.getByTestId("saved-searches-panel")).toBeVisible();
}

// Tests ------------------------------------------------------------------

test.describe("Panneau Mes Recherches", () => {
  test("visible uniquement quand l'utilisateur est connecté", async ({ page }) => {
    await gotoHome(page);
    await expect(page.getByTestId("btn-saved-searches")).not.toBeVisible();

    await registerAndLogin(page, uniqueEmail(), "password123");
    await expect(page.getByTestId("btn-saved-searches")).toBeVisible();
  });

  test("s'ouvre et se ferme au clic", async ({ page }) => {
    await gotoHome(page);
    await registerAndLogin(page, uniqueEmail(), "password123");

    await page.getByTestId("btn-saved-searches").click();
    await expect(page.getByTestId("saved-searches-panel")).toBeVisible();

    // Fermer via clic à l'extérieur du panel (sur le logo dans le header)
    await page.locator("header").click({ position: { x: 20, y: 20 } });
    await expect(page.getByTestId("saved-searches-panel")).not.toBeVisible({ timeout: 5000 });
  });

  test("affiche le message 'aucune recherche' par défaut", async ({ page }) => {
    await gotoHome(page);
    await registerAndLogin(page, uniqueEmail(), "password123");

    await openSavedSearchesPanel(page);
    await expect(
      page.getByTestId("saved-searches-panel").getByText(/aucune recherche|no saved/i)
    ).toBeVisible();
  });
});

test.describe("Sauvegarder une recherche", () => {
  test("le bouton Sauvegarder apparaît après une recherche", async ({ page }) => {
    await gotoHome(page);
    await registerAndLogin(page, uniqueEmail(), "password123");
    await doSearch(page, "histoire");

    await openSavedSearchesPanel(page);
    await expect(page.getByTestId("btn-show-save-form")).toBeVisible();
  });

  test("sauvegarder une recherche simple — elle apparaît dans la liste", async ({ page }) => {
    await gotoHome(page);
    const email = uniqueEmail();
    await registerAndLogin(page, email, "password123");
    await doSearch(page, "philosophie");

    await openSavedSearchesPanel(page);
    await page.getByTestId("btn-show-save-form").click();

    // Formulaire de nom
    await expect(page.getByTestId("input-search-name")).toBeVisible();
    await page.getByTestId("input-search-name").fill("Ma recherche philosophie");
    await page.getByTestId("btn-save-confirm").click();

    // La recherche apparaît dans la liste
    await expect(
      page.getByTestId("saved-searches-panel").getByText("Ma recherche philosophie")
    ).toBeVisible({ timeout: 5000 });
  });

  test("sauvegarder via la touche Entrée dans le champ de nom", async ({ page }) => {
    await gotoHome(page);
    await registerAndLogin(page, uniqueEmail(), "password123");
    await doSearch(page, "littérature");

    await openSavedSearchesPanel(page);
    await page.getByTestId("btn-show-save-form").click();
    await page.getByTestId("input-search-name").fill("Littérature test");
    await page.getByTestId("input-search-name").press("Enter");

    await expect(
      page.getByTestId("saved-searches-panel").getByText("Littérature test")
    ).toBeVisible({ timeout: 5000 });
  });

  test("le bouton Sauvegarder est désactivé si le nom est vide", async ({ page }) => {
    await gotoHome(page);
    await registerAndLogin(page, uniqueEmail(), "password123");
    await doSearch(page, "art");

    await openSavedSearchesPanel(page);
    await page.getByTestId("btn-show-save-form").click();
    // Le champ est vide → bouton désactivé
    await expect(page.getByTestId("btn-save-confirm")).toBeDisabled();
  });

  test("impossible de sauvegarder sans recherche active — bouton absent", async ({ page }) => {
    await gotoHome(page);
    await registerAndLogin(page, uniqueEmail(), "password123");

    await openSavedSearchesPanel(page);
    // Pas de recherche active → bouton Sauvegarder absent
    await expect(page.getByTestId("btn-show-save-form")).not.toBeVisible();
  });
});

test.describe("Charger une recherche sauvegardée", () => {
  test("charger restitue le terme de recherche et lance la recherche", async ({ page }) => {
    await gotoHome(page);
    await registerAndLogin(page, uniqueEmail(), "password123");

    // Faire une recherche et la sauvegarder
    await doSearch(page, "sociologie");
    await openSavedSearchesPanel(page);
    await page.getByTestId("btn-show-save-form").click();
    await page.getByTestId("input-search-name").fill("Sociologie test");
    await page.getByTestId("btn-save-confirm").click();
    await expect(
      page.getByTestId("saved-searches-panel").getByText("Sociologie test")
    ).toBeVisible({ timeout: 5000 });

    // Fermer le panel
    await page.mouse.click(10, 10);
    await expect(page.getByTestId("saved-searches-panel")).not.toBeVisible();

    // Effacer la recherche courante
    await page.evaluate(() => window.scrollTo(0, 0));
    const searchInput = page.getByPlaceholder(/Rechercher|Search/i).first();
    await searchInput.fill("");

    // Charger la recherche sauvegardée
    await page.getByTestId("btn-saved-searches").click();
    const loadBtn = page.locator("[data-testid^='btn-load-search-']").first();
    await loadBtn.click();

    // Vérifier que le terme est restauré ET que les résultats s'affichent
    await expect(searchInput).toHaveValue("sociologie", { timeout: 5000 });
    await waitForResults(page);
  });

  test("charger depuis un nouvel onglet (après reload) exécute la recherche", async ({ page }) => {
    await gotoHome(page);
    const email = uniqueEmail();
    await registerAndLogin(page, email, "password123");

    // Sauvegarder une recherche
    await doSearch(page, "histoire");
    await openSavedSearchesPanel(page);
    await page.getByTestId("btn-show-save-form").click();
    await page.getByTestId("input-search-name").fill("Histoire persistée");
    await page.getByTestId("btn-save-confirm").click();
    await expect(
      page.getByTestId("saved-searches-panel").getByText("Histoire persistée")
    ).toBeVisible({ timeout: 5000 });

    // Recharger la page (la session JWT persiste via localStorage)
    await page.reload();
    await expect(page.locator("header")).toBeVisible({ timeout: 15000 });

    // Ouvrir le panel et charger la recherche
    await openSavedSearchesPanel(page);
    await expect(
      page.getByTestId("saved-searches-panel").getByText("Histoire persistée")
    ).toBeVisible({ timeout: 5000 });
    const loadBtn = page.locator("[data-testid^='btn-load-search-']").first();
    await loadBtn.click();

    // Vérifier que le terme est restauré et que les résultats s'affichent
    const searchInput = page.getByPlaceholder(/Rechercher|Search/i).first();
    await expect(searchInput).toHaveValue("histoire", { timeout: 5000 });
    await waitForResults(page);
  });
});

test.describe("Supprimer une recherche sauvegardée", () => {
  test("supprimer retire la recherche de la liste", async ({ page }) => {
    await gotoHome(page);
    await registerAndLogin(page, uniqueEmail(), "password123");

    // Sauvegarder
    await doSearch(page, "économie");
    await openSavedSearchesPanel(page);
    await page.getByTestId("btn-show-save-form").click();
    await page.getByTestId("input-search-name").fill("Économie à supprimer");
    await page.getByTestId("btn-save-confirm").click();
    await expect(
      page.getByTestId("saved-searches-panel").getByText("Économie à supprimer")
    ).toBeVisible({ timeout: 5000 });

    // Survoler pour faire apparaître le bouton supprimer et cliquer
    const item = page.getByTestId("saved-searches-panel").getByText("Économie à supprimer");
    await item.hover();
    const deleteBtn = page.locator("[data-testid^='btn-delete-search-']").first();
    await deleteBtn.click({ force: true });

    // La recherche disparaît
    await expect(
      page.getByTestId("saved-searches-panel").getByText("Économie à supprimer")
    ).not.toBeVisible({ timeout: 5000 });
  });
});

test.describe("Persistance après rechargement", () => {
  test("les recherches sauvegardées sont toujours présentes après reload", async ({ page }) => {
    await gotoHome(page);
    await registerAndLogin(page, uniqueEmail(), "password123");

    await doSearch(page, "géographie");
    await openSavedSearchesPanel(page);
    await page.getByTestId("btn-show-save-form").click();
    await page.getByTestId("input-search-name").fill("Géographie persistée");
    await page.getByTestId("btn-save-confirm").click();
    await expect(
      page.getByTestId("saved-searches-panel").getByText("Géographie persistée")
    ).toBeVisible({ timeout: 5000 });

    // Recharger la page
    await page.reload();
    await expect(page.locator("header")).toBeVisible({ timeout: 15000 });

    // Vérifier que la recherche est toujours là
    await openSavedSearchesPanel(page);
    await expect(
      page.getByTestId("saved-searches-panel").getByText("Géographie persistée")
    ).toBeVisible({ timeout: 5000 });
  });
});
