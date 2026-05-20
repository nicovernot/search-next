import { test, expect } from '@playwright/test';

const HYPERMEDIA_BASE = process.env.HYPERMEDIA_URL ?? 'http://localhost:8000/api/v1/hypermedia';

test.describe('Frontend hypermedia (HTMX)', () => {
  test('La page d\'accueil charge et affiche le formulaire de recherche', async ({ page }) => {
    await page.goto(`${HYPERMEDIA_BASE}/`);
    await expect(page.locator('#search-form')).toBeVisible();
    await expect(page.locator('#search-input')).toBeVisible();
    await expect(page.getByRole('button', { name: /Rechercher/i })).toBeVisible();
  });

  test('Une recherche met à jour les résultats sans rechargement de page', async ({ page }) => {
    await page.goto(`${HYPERMEDIA_BASE}/`);
    await page.fill('#search-input', 'histoire');
    await page.click('button[type=submit]');

    // HTMX remplace le contenu de #search-results
    await expect(page.locator('#search-results')).not.toBeEmpty({ timeout: 10000 });
  });

  test('L\'URL est mise à jour via hx-push-url après une recherche', async ({ page }) => {
    await page.goto(`${HYPERMEDIA_BASE}/`);
    await page.fill('#search-input', 'histoire');
    await page.click('button[type=submit]');

    await page.waitForURL(/q=histoire/, { timeout: 10000 });
    expect(page.url()).toContain('q=histoire');
  });

  test('La pagination navigue vers la page suivante', async ({ page }) => {
    await page.goto(`${HYPERMEDIA_BASE}/search?q=science`);
    const nextButton = page.getByRole('button', { name: /Suivant/i });

    if (await nextButton.isVisible()) {
      await nextButton.click();
      await page.waitForURL(/page=2/, { timeout: 10000 });
      expect(page.url()).toContain('page=2');
    } else {
      test.skip(true, 'Pas assez de résultats pour tester la pagination');
    }
  });

  test('Le dark mode bascule via Alpine.js', async ({ page }) => {
    await page.goto(`${HYPERMEDIA_BASE}/`);
    const html = page.locator('html');
    const toggle = page.getByRole('button', { name: /Basculer le thème/i });

    await toggle.click();
    await expect(html).toHaveClass(/dark/, { timeout: 2000 });

    await toggle.click();
    await expect(html).not.toHaveClass(/dark/, { timeout: 2000 });
  });

  test('Le retour navigateur restaure la recherche précédente', async ({ page }) => {
    await page.goto(`${HYPERMEDIA_BASE}/`);
    await page.fill('#search-input', 'histoire');
    await page.click('button[type=submit]');
    await page.waitForURL(/q=histoire/, { timeout: 10000 });

    await page.fill('#search-input', 'science');
    await page.click('button[type=submit]');
    await page.waitForURL(/q=science/, { timeout: 10000 });

    await page.goBack();
    expect(page.url()).toContain('q=histoire');
  });
});
