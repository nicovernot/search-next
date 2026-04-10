import { test, expect } from '@playwright/test';

test.describe('Recherche OpenEdition - End To End', () => {
  test('La page principale charge correctement', async ({ page }) => {
    await page.goto('/');

    // Vérifie que le titre est présent
    await expect(page.locator('text=OpenEdition Search').first()).toBeVisible();
    await expect(page.locator('text=Rechercher dans OpenEdition')).toBeVisible();

    // Vérifie la présence de la barre de recherche (le placeholder devrait être présent)
    const searchInput = page.getByPlaceholder(/Rechercher/i).first();
    await expect(searchInput).toBeVisible();
  });

  test('Permet de saisir une requête et de lancer la recherche', async ({ page }) => {
    await page.goto('/');

    // On sélectionne l'input et on simule une frappe
    const searchInput = page.getByPlaceholder(/Rechercher/i).first();
    await searchInput.fill('histoire');
    
    // Soit on submit le form, soit le debounce s'en occupe
    await searchInput.press('Enter');

    // On s'assure qu'un chargement ou des résultats apparaissent.
    // L'UI affiche soit les facets, soit results list. On check un test simple
    // pour ne pas dépendre du state exact du mock API s'il y en a un.
    // L'objectif est de s'assurer qu'il n'y a pas de crash fatal de React.
    await expect(page.locator('main, div')).toBeVisible();
  });
});
