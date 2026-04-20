import { test, expect } from "@playwright/test";

/**
 * Tests E2E — spec 005-permissions
 * Vérifie que les badges d'accès apparaissent sur les résultats de recherche.
 *
 * Stratégie : on intercepte les deux routes (search + permissions) avec des
 * données déterministes pour tester chaque statut indépendamment du backend.
 */

const SEARCH_URL = "**/search";
const PERMISSIONS_URL = "**/permissions**";

const FAKE_DOC = {
  url: "https://journals.openedition.org/test/123",
  titre: "Article de test permissions",
  site_title: "OpenEdition Journals",
  type: "article",
  anneedatepubli: "2023",
};

const FAKE_SEARCH_RESPONSE = {
  results: [FAKE_DOC],
  total: 1,
  facets: {},
};

test.describe("Badges d'accès sur les résultats", () => {
  test("Badge 'open access' quand isPermitted=true sans abonnement", async ({ page }) => {
    await page.route(SEARCH_URL, (route) => {
      route.fulfill({ json: FAKE_SEARCH_RESPONSE });
    });
    await page.route(PERMISSIONS_URL, (route) => {
      route.fulfill({
        json: {
          data: {
            organization: null,
            docs: [{ url: FAKE_DOC.url, isPermitted: true }],
          },
          info: {},
        },
      });
    });

    await page.goto("/fr/");
    await page.getByPlaceholder(/Search|Rechercher/i).first().fill("test");
    await page.getByPlaceholder(/Search|Rechercher/i).first().press("Enter");

    await expect(page.locator('[data-testid="result-item"]').first()).toBeVisible({ timeout: 10000 });
    await expect(page.locator('[data-testid="perm-badge-open"]').first()).toBeVisible({ timeout: 5000 });
  });

  test("Badge 'restricted' quand isPermitted=false", async ({ page }) => {
    await page.route(SEARCH_URL, (route) => {
      route.fulfill({ json: FAKE_SEARCH_RESPONSE });
    });
    await page.route(PERMISSIONS_URL, (route) => {
      route.fulfill({
        json: {
          data: {
            organization: null,
            docs: [{ url: FAKE_DOC.url, isPermitted: false }],
          },
          info: {},
        },
      });
    });

    await page.goto("/fr/");
    await page.getByPlaceholder(/Search|Rechercher/i).first().fill("test");
    await page.getByPlaceholder(/Search|Rechercher/i).first().press("Enter");

    await expect(page.locator('[data-testid="result-item"]').first()).toBeVisible({ timeout: 10000 });
    await expect(page.locator('[data-testid="perm-badge-restricted"]').first()).toBeVisible({ timeout: 5000 });
  });

  test("Badge 'institutional' quand isPermitted=true avec purchased=true", async ({ page }) => {
    await page.route(SEARCH_URL, (route) => {
      route.fulfill({ json: FAKE_SEARCH_RESPONSE });
    });
    await page.route(PERMISSIONS_URL, (route) => {
      route.fulfill({
        json: {
          data: {
            organization: { purchased: true, shortname: "TestOrg" },
            docs: [{ url: FAKE_DOC.url, isPermitted: true }],
          },
          info: {},
        },
      });
    });

    await page.goto("/fr/");
    await page.getByPlaceholder(/Search|Rechercher/i).first().fill("test");
    await page.getByPlaceholder(/Search|Rechercher/i).first().press("Enter");

    await expect(page.locator('[data-testid="result-item"]').first()).toBeVisible({ timeout: 10000 });
    await expect(page.locator('[data-testid="perm-badge-institutional"]').first()).toBeVisible({ timeout: 5000 });
  });

  test("Aucun badge si l'API permissions échoue (mode dégradé silencieux)", async ({ page }) => {
    await page.route(SEARCH_URL, (route) => {
      route.fulfill({ json: FAKE_SEARCH_RESPONSE });
    });
    await page.route(PERMISSIONS_URL, (route) => {
      route.abort("failed");
    });

    await page.goto("/fr/");
    await page.getByPlaceholder(/Search|Rechercher/i).first().fill("test");
    await page.getByPlaceholder(/Search|Rechercher/i).first().press("Enter");

    await expect(page.locator('[data-testid="result-item"]').first()).toBeVisible({ timeout: 10000 });
    // Aucun badge ne doit apparaître
    await expect(page.locator('[data-testid^="perm-badge-"]')).toHaveCount(0);
  });
});
