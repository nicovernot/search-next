/**
 * Tests E2E — spec 004 : URL Sync
 *
 * Vérifie la synchronisation bidirectionnelle entre l'état de recherche et l'URL :
 *  - URL mise à jour après chaque interaction (query, mode, filtre, page)
 *  - Hydratation depuis l'URL au chargement de la page
 *
 * Toutes les réponses API sont mockées pour rendre les tests déterministes.
 */

import { test, expect, Page } from "@playwright/test";

// ── Constantes ───────────────────────────────────────────────────────────────

const SEARCH_URL = "**/search";
const FACETS_CONFIG_URL = "**/facets/config";
const PERMISSIONS_URL = "**/api/permissions**";

const FAKE_DOC = {
  url: "https://journals.openedition.org/test/123",
  titre: "Article de test URL Sync",
  site_title: "OpenEdition Journals",
  type: "article",
  anneedatepubli: "2023",
  platformID: "journals",
};

// total=42 → 5 pages (10 résultats par page) → boutons de pagination visibles
const FAKE_SEARCH_RESPONSE = {
  results: [FAKE_DOC],
  total: 42,
  facets: {
    platform: {
      buckets: [
        { key: "journals", doc_count: 30 },
        { key: "books", doc_count: 12 },
      ],
    },
  },
};

const FAKE_FACETS_CONFIG = {
  search_fields: ["titre"],
  common: { platform: {} },
};

// ── Helpers ───────────────────────────────────────────────────────────────────

async function mockApis(page: Page) {
  await page.route(FACETS_CONFIG_URL, (route) =>
    route.fulfill({ json: FAKE_FACETS_CONFIG })
  );
  await page.route(SEARCH_URL, (route) =>
    route.fulfill({ json: FAKE_SEARCH_RESPONSE })
  );
  await page.route(PERMISSIONS_URL, (route) =>
    route.fulfill({ json: { data: { organization: null, docs: [] }, info: {} } })
  );
}

async function waitForResults(page: Page) {
  await expect(
    page.locator('[data-testid="result-item"]').first()
  ).toBeVisible({ timeout: 10000 });
}

async function doSearch(page: Page, query: string) {
  const input = page.getByPlaceholder(/Search|Rechercher/i).first();
  await input.fill(query);
  await input.press("Enter");
  await waitForResults(page);
}

// ── Tests : URL mise à jour sur interaction ───────────────────────────────────

test.describe("URL mise à jour sur interaction utilisateur", () => {
  test("après une recherche simple → URL contient ?q=...", async ({ page }) => {
    await mockApis(page);
    await page.goto("/fr/");

    await doSearch(page, "histoire");

    await expect(page).toHaveURL(/[?&]q=histoire/, { timeout: 5000 });
  });

  test("passer en mode avancé → URL contient mode=advanced", async ({ page }) => {
    await mockApis(page);
    await page.goto("/fr/");

    await page.getByText(/Recherche avancée|Advanced search/i).click();

    await expect(page).toHaveURL(/[?&]mode=advanced/, { timeout: 5000 });
  });

  test("revenir en mode simple → mode retiré de l'URL", async ({ page }) => {
    await mockApis(page);
    await page.goto("/fr/?mode=advanced");

    // S'assurer que l'URL contient bien mode=advanced au départ
    await expect(page).toHaveURL(/mode=advanced/);

    // Cliquer sur "Recherche simple"
    await page.getByText(/Recherche simple|Simple search/i).click();

    // mode=advanced doit disparaître de l'URL
    await expect(page).not.toHaveURL(/mode=advanced/, { timeout: 5000 });
  });

  test("cliquer sur un filtre de facette → URL contient f_platform=...", async ({ page }) => {
    await mockApis(page);
    await page.goto("/fr/");
    await doSearch(page, "test");

    // Cliquer sur la première checkbox de facette (valeur "journals")
    const checkbox = page.locator('input[type="checkbox"]').first();
    await expect(checkbox).toBeVisible({ timeout: 5000 });
    await checkbox.click();

    await expect(page).toHaveURL(/f_platform=journals/, { timeout: 5000 });
  });

  test("aller à la page 2 → URL contient page=2", async ({ page }) => {
    await mockApis(page);
    await page.goto("/fr/");
    await doSearch(page, "philosophie");

    // Cliquer sur le bouton page 2 dans la pagination
    const pageButton = page.locator('[data-testid="pagination-page-2"]');
    await expect(pageButton).toBeVisible({ timeout: 5000 });
    await pageButton.click();

    await expect(page).toHaveURL(/[?&]page=2/, { timeout: 5000 });
  });
});

// ── Tests : Hydratation depuis l'URL ─────────────────────────────────────────

test.describe("Hydratation de l'état depuis l'URL", () => {
  test("URL ?q=test → recherche déclenchée et input pré-rempli", async ({ page }) => {
    await mockApis(page);
    await page.goto("/fr/?q=histoire");

    // La recherche doit être déclenchée automatiquement
    await waitForResults(page);

    // L'input doit contenir la query de l'URL
    const input = page.getByPlaceholder(/Search|Rechercher/i).first();
    await expect(input).toHaveValue("histoire", { timeout: 5000 });
  });

  test("URL ?mode=advanced → mode avancé activé", async ({ page }) => {
    await mockApis(page);
    await page.goto("/fr/?mode=advanced");

    await expect(page.locator("header")).toBeVisible({ timeout: 10000 });

    // Le bouton "Recherche avancée" doit être actif (classe bg-highlight)
    const advancedBtn = page.getByText(/Recherche avancée|Advanced search/i);
    await expect(advancedBtn).toHaveClass(/bg-highlight/, { timeout: 5000 });
  });

  test("URL ?q=test&f_platform=journals → filtre actif affiché", async ({ page }) => {
    await mockApis(page);
    await page.goto("/fr/?q=test&f_platform=journals");

    await waitForResults(page);

    // Le chip de filtre actif doit être affiché dans la sidebar des facettes
    await expect(page.locator('[data-testid="active-filter-chip"]').first()).toBeVisible({ timeout: 5000 });
  });

  test("URL ?q=test&page=2 → page 2 affichée, requête lancée", async ({ page }) => {
    await mockApis(page);
    await page.goto("/fr/?q=test&page=2");

    await waitForResults(page);

    // Le bouton de page 2 doit être actif (classe bg-highlight)
    const page2Btn = page.locator('[data-testid="pagination-page-2"]');
    await expect(page2Btn).toHaveClass(/bg-highlight/, { timeout: 5000 });
  });

  test("rechargement de page → état de recherche restauré depuis l'URL", async ({ page }) => {
    await mockApis(page);
    await page.goto("/fr/");
    await doSearch(page, "sociologie");
    await expect(page).toHaveURL(/q=sociologie/, { timeout: 5000 });

    // Recharger la page
    await mockApis(page);
    await page.reload();

    // La recherche doit être restaurée
    const input = page.getByPlaceholder(/Search|Rechercher/i).first();
    await expect(input).toHaveValue("sociologie", { timeout: 10000 });
    await waitForResults(page);
  });
});
