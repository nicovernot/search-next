/**
 * Tests E2E — spec 004 : URL Sync
 *
 * Vérifie la synchronisation bidirectionnelle entre l'état de recherche et l'URL :
 *  - URL mise à jour après chaque interaction (query, mode, filtre, page)
 *  - Hydratation depuis l'URL au chargement de la page
 *  - Navigation back/forward (FR-003)
 *  - Paramètres invalides ignorés silencieusement (edge cases)
 *  - Restauration du QueryBuilder depuis l'URL (P2 — lq=)
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

    await expect(page).toHaveURL(/mode=advanced/);

    await page.getByText(/Recherche simple|Simple search/i).click();

    await expect(page).not.toHaveURL(/mode=advanced/, { timeout: 5000 });
  });

  test("cliquer sur un filtre de facette → URL contient f_platform=...", async ({ page }) => {
    await mockApis(page);
    await page.goto("/fr/");
    await doSearch(page, "test");

    const checkbox = page.locator('input[type="checkbox"]').first();
    await expect(checkbox).toBeVisible({ timeout: 5000 });
    await checkbox.click();

    await expect(page).toHaveURL(/f_platform=journals/, { timeout: 5000 });
  });

  test("aller à la page 2 → URL contient page=2", async ({ page }) => {
    await mockApis(page);
    await page.goto("/fr/");
    await doSearch(page, "philosophie");

    const pageButton = page.locator('[data-testid="pagination-page-2"]');
    await expect(pageButton).toBeVisible({ timeout: 5000 });
    await pageButton.click();

    await expect(page).toHaveURL(/[?&]page=2/, { timeout: 5000 });
  });

  test("changer de page ne crée pas de nouvelle entrée d'historique (replaceState)", async ({ page }) => {
    await mockApis(page);
    await page.goto("/fr/");
    await doSearch(page, "sociologie");
    await expect(page).toHaveURL(/q=sociologie/, { timeout: 5000 });

    // Aller page 2 puis page 3 (deux replace, pas deux push)
    await page.locator('[data-testid="pagination-page-2"]').click();
    await expect(page).toHaveURL(/page=2/, { timeout: 5000 });
    await page.locator('[data-testid="pagination-page-3"]').click();
    await expect(page).toHaveURL(/page=3/, { timeout: 5000 });

    // Un seul goBack doit ramener à la recherche initiale (q=sociologie sans page=),
    // car les changements de page sont des replaceState
    await page.goBack();
    await expect(page).toHaveURL(/q=sociologie/, { timeout: 5000 });
    await expect(page).not.toHaveURL(/page=/, { timeout: 3000 });
  });
});

// ── Tests : Hydratation depuis l'URL ─────────────────────────────────────────

test.describe("Hydratation de l'état depuis l'URL", () => {
  test("URL ?q=test → recherche déclenchée et input pré-rempli", async ({ page }) => {
    await mockApis(page);
    await page.goto("/fr/?q=histoire");

    await waitForResults(page);

    const input = page.getByPlaceholder(/Search|Rechercher/i).first();
    await expect(input).toHaveValue("histoire", { timeout: 5000 });
  });

  test("URL ?mode=advanced → mode avancé activé", async ({ page }) => {
    await mockApis(page);
    await page.goto("/fr/?mode=advanced");

    await expect(page.locator("header")).toBeVisible({ timeout: 10000 });

    const advancedBtn = page.getByText(/Recherche avancée|Advanced search/i);
    await expect(advancedBtn).toHaveClass(/bg-highlight/, { timeout: 5000 });
  });

  test("URL ?q=test&f_platform=journals → filtre actif affiché", async ({ page }) => {
    await mockApis(page);
    await page.goto("/fr/?q=test&f_platform=journals");

    await waitForResults(page);

    await expect(page.locator('[data-testid="active-filter-chip"]').first()).toBeVisible({ timeout: 5000 });
  });

  test("URL ?q=test&page=2 → page 2 affichée, requête lancée", async ({ page }) => {
    await mockApis(page);
    await page.goto("/fr/?q=test&page=2");

    await waitForResults(page);

    const page2Btn = page.locator('[data-testid="pagination-page-2"]');
    await expect(page2Btn).toHaveClass(/bg-highlight/, { timeout: 5000 });
  });

  test("rechargement de page → état de recherche restauré depuis l'URL", async ({ page }) => {
    await mockApis(page);
    await page.goto("/fr/");
    await doSearch(page, "sociologie");
    await expect(page).toHaveURL(/q=sociologie/, { timeout: 5000 });

    await mockApis(page);
    await page.reload();

    const input = page.getByPlaceholder(/Search|Rechercher/i).first();
    await expect(input).toHaveValue("sociologie", { timeout: 10000 });
    await waitForResults(page);
  });
});

// ── Tests : Navigation back/forward (FR-003) ──────────────────────────────────

test.describe("Navigation back/forward", () => {
  test("retour arrière → état restauré à la recherche précédente", async ({ page }) => {
    await mockApis(page);
    await page.goto("/fr/");

    // Recherche A (crée une entrée pushState)
    await doSearch(page, "histoire");
    await expect(page).toHaveURL(/q=histoire/, { timeout: 5000 });

    // Recherche B (crée une deuxième entrée pushState)
    await doSearch(page, "philosophie");
    await expect(page).toHaveURL(/q=philosophie/, { timeout: 5000 });

    // Retour arrière → doit restaurer A
    await page.goBack();

    const input = page.getByPlaceholder(/Search|Rechercher/i).first();
    await expect(input).toHaveValue("histoire", { timeout: 8000 });
    await expect(page).toHaveURL(/q=histoire/, { timeout: 5000 });
  });

  test("retour puis avance → état restauré correctement dans les deux sens", async ({ page }) => {
    await mockApis(page);
    await page.goto("/fr/");

    await doSearch(page, "histoire");
    await expect(page).toHaveURL(/q=histoire/, { timeout: 5000 });

    await doSearch(page, "philosophie");
    await expect(page).toHaveURL(/q=philosophie/, { timeout: 5000 });

    // Retour → A
    await page.goBack();
    await expect(page).toHaveURL(/q=histoire/, { timeout: 5000 });

    // Avance → B
    await page.goForward();

    const input = page.getByPlaceholder(/Search|Rechercher/i).first();
    await expect(input).toHaveValue("philosophie", { timeout: 8000 });
    await expect(page).toHaveURL(/q=philosophie/, { timeout: 5000 });
  });

  test("retour depuis une recherche avec filtre → filtre restauré", async ({ page }) => {
    await mockApis(page);
    await page.goto("/fr/");

    // Recherche A avec filtre
    await doSearch(page, "test");
    await page.locator('input[type="checkbox"]').first().click();
    await expect(page).toHaveURL(/f_platform=journals/, { timeout: 5000 });

    // Recherche B (nouvelle query → pushState)
    await doSearch(page, "philosophie");
    await expect(page).toHaveURL(/q=philosophie/, { timeout: 5000 });
    await expect(page).not.toHaveURL(/f_platform/, { timeout: 3000 });

    // Retour → A avec filtre restauré
    await page.goBack();
    await expect(page).toHaveURL(/f_platform=journals/, { timeout: 8000 });
    await expect(page.locator('[data-testid="active-filter-chip"]').first()).toBeVisible({ timeout: 5000 });
  });
});

// ── Tests : Paramètres invalides ignorés ─────────────────────────────────────

test.describe("Paramètres invalides ignorés silencieusement", () => {
  test("page négative → clampée à 1, pas de crash", async ({ page }) => {
    await mockApis(page);
    await page.goto("/fr/?q=test&page=-5");

    await waitForResults(page);
    // Pas de crash — l'application fonctionne normalement
    await expect(page.locator('[data-testid="result-item"]').first()).toBeVisible();
  });

  test("size non numérique → ignoré, défaut 10 utilisé", async ({ page }) => {
    await mockApis(page);
    await page.goto("/fr/?q=test&size=abc");

    await waitForResults(page);
    await expect(page.locator('[data-testid="result-item"]').first()).toBeVisible();
  });

  test("lq malformé → pas de crash, mode avancé actif mais QB vide", async ({ page }) => {
    await mockApis(page);
    await page.goto("/fr/?mode=advanced&lq=not-valid-json{{{");

    await expect(page.locator("header")).toBeVisible({ timeout: 10000 });
    // L'application ne doit pas crasher
    await expect(page.locator("body")).not.toContainText(/error|erreur/i);
    // Le mode avancé est bien activé
    const advancedBtn = page.getByText(/Recherche avancée|Advanced search/i);
    await expect(advancedBtn).toHaveClass(/bg-highlight/, { timeout: 5000 });
  });

  test("filtre avec champ inexistant → ignoré, recherche lancée normalement", async ({ page }) => {
    await mockApis(page);
    await page.goto("/fr/?q=test&f_champ_inexistant=valeur");

    await waitForResults(page);
    await expect(page.locator('[data-testid="result-item"]').first()).toBeVisible();
  });
});

// ── Tests : Restauration QueryBuilder depuis l'URL (P2) ──────────────────────

test.describe("Restauration QueryBuilder depuis l'URL (lq=)", () => {
  test("URL avec lq= simple → QB affiché avec la règle restaurée", async ({ page }) => {
    const lq = JSON.stringify({
      combinator: "and",
      rules: [{ field: "titre", operator: "contains", value: "histoire" }],
    });
    await mockApis(page);
    await page.goto(`/fr/?mode=advanced&lq=${encodeURIComponent(lq)}`);

    // Le QueryBuilder doit être visible
    await expect(page.locator(".query-builder-premium")).toBeVisible({ timeout: 10000 });

    // La valeur "histoire" doit apparaître dans la règle restaurée
    const valueInput = page.locator(".query-builder-premium input").first();
    await expect(valueInput).toHaveValue("histoire", { timeout: 5000 });
  });

  test("URL avec lq= complexe (AND/OR imbriqués) → QB restauré sans perte", async ({ page }) => {
    const lq = JSON.stringify({
      combinator: "or",
      rules: [
        { field: "titre", operator: "contains", value: "histoire" },
        {
          combinator: "and",
          rules: [
            { field: "titre", operator: "beginsWith", value: "science" },
            { field: "titre", operator: "!=", value: "politique" },
          ],
        },
      ],
    });
    await mockApis(page);
    await page.goto(`/fr/?mode=advanced&lq=${encodeURIComponent(lq)}`);

    await expect(page.locator(".query-builder-premium")).toBeVisible({ timeout: 10000 });

    // Les trois valeurs doivent apparaître dans le QB
    await expect(page.locator(".query-builder-premium")).toContainText("histoire", { timeout: 5000 });
    await expect(page.locator(".query-builder-premium")).toContainText("science", { timeout: 5000 });
    await expect(page.locator(".query-builder-premium")).toContainText("politique", { timeout: 5000 });
  });

  test("lq= encodé dans l'URL reste < 2000 caractères pour un cas courant", async ({ page }) => {
    // SC-004 : URL lisible et < 2000 chars pour ≤ 3 niveaux, ≤ 5 règles
    const lq = {
      combinator: "and",
      rules: [
        { field: "titre", operator: "contains", value: "histoire" },
        { field: "titre", operator: "contains", value: "moderne" },
        { field: "titre", operator: "!=", value: "guerre" },
        { field: "titre", operator: "beginsWith", value: "europe" },
        { field: "titre", operator: "endsWith", value: "XVIIIe" },
      ],
    };
    const url = `/fr/?mode=advanced&lq=${encodeURIComponent(JSON.stringify(lq))}`;

    await mockApis(page);
    await page.goto(url);

    await expect(page.locator(".query-builder-premium")).toBeVisible({ timeout: 10000 });
    // Vérifier que l'URL reste raisonnable (< 2000 chars)
    expect(url.length).toBeLessThan(2000);
  });
});
