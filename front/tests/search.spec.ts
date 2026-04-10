import { test, expect } from '@playwright/test';

test.describe('Recherche OpenEdition - End To End', () => {
  test('La page principale charge correctement', async ({ page }) => {
    await page.goto('/');

    // Vérifie que la marque est présente (utilisation d'un regex plus large pour éviter les problèmes de span)
    await expect(page.locator('header').filter({ hasText: /OpenEdition Search/i })).toBeVisible();
    await expect(page.getByText(/Rechercher/i).first()).toBeVisible();

    // Vérifie la présence de la barre de recherche (support FR/EN)
    const searchInput = page.getByPlaceholder(/Search|Rechercher/i).first();
    await expect(searchInput).toBeVisible();
  });

  test('Permet de saisir une requête et de lancer la recherche', async ({ page }) => {
    await page.goto('/');

    // On sélectionne l'input (support FR/EN)
    const searchInput = page.getByPlaceholder(/Search|Rechercher/i).first();
    await searchInput.fill('histoire');
    
    await searchInput.press('Enter');

    // On s'assure que les résultats ou le conteneur principal sont chargés
    await expect(page.locator('article, .animate-fade-in')).toBeVisible({ timeout: 10000 });
  });
});
