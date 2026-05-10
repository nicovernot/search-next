# Corpus d'évaluation — Recherche lexicale vs hybride

**Spec** : 012-semantic-search-api-platform — Phase 0  
**Objectif** : constituer ≥ 50 requêtes métier représentatives pour mesurer le gain de la recherche hybride vs lexicale pure.  
**Statut** : ⚪ Template — à renseigner par les équipes métier avant Phase 4.

---

## Mode d'emploi

Pour chaque requête :
- **query** : la requête telle que saisie par un utilisateur réel
- **mode_attendu** : `lexical` (mots-clés exacts) ou `hybride` (intention sémantique, reformulations, synonymes)
- **resultats_attendus** : ≥ 3 `doc_id` Solr qui doivent apparaître dans le top-10
- **resultats_absents** : `doc_id` qui ne doivent PAS remonter (faux positifs connus)
- **commentaire** : contexte métier, difficulté, cas particulier

Les requêtes doivent couvrir :
- [ ] Tous les types de documents (article, livre, chapitre, billet de blog, événement)
- [ ] Toutes les plateformes (OJ, OB, HO, CO)
- [ ] Plusieurs disciplines
- [ ] Requêtes courtes (1-2 mots) et longues (phrase)
- [ ] Requêtes en français et en anglais
- [ ] Requêtes conceptuelles sans mot-clé exact (cas hybride fort)
- [ ] Requêtes par auteur, par revue
- [ ] Requêtes avec accents / sans accents

---

## Requêtes — à compléter

### Bloc A — Requêtes lexicales simples (mots-clés exacts)
> Mode attendu : `lexical` — la recherche Solr actuelle doit déjà bien répondre.

| # | query | mode_attendu | resultats_attendus | commentaire |
|---|---|---|---|---|
| A01 | | lexical | | |
| A02 | | lexical | | |
| A03 | | lexical | | |
| A04 | | lexical | | |
| A05 | | lexical | | |
| A06 | | lexical | | |
| A07 | | lexical | | |
| A08 | | lexical | | |
| A09 | | lexical | | |
| A10 | | lexical | | |

### Bloc B — Requêtes sémantiques / conceptuelles
> Mode attendu : `hybride` — la recherche lexicale actuelle rate ces cas, la hybride devrait les trouver.

| # | query | mode_attendu | resultats_attendus | commentaire |
|---|---|---|---|---|
| B01 | | hybride | | Reformulation : synonyme non présent dans le texte |
| B02 | | hybride | | Concept abstrait sans mot-clé direct |
| B03 | | hybride | | Requête en anglais sur contenu en français |
| B04 | | hybride | | Requête en français sur contenu en anglais |
| B05 | | hybride | | |
| B06 | | hybride | | |
| B07 | | hybride | | |
| B08 | | hybride | | |
| B09 | | hybride | | |
| B10 | | hybride | | |
| B11 | | hybride | | |
| B12 | | hybride | | |
| B13 | | hybride | | |
| B14 | | hybride | | |
| B15 | | hybride | | |

### Bloc C — Requêtes par discipline
> Couvrir chaque discipline de la taxonomie avec ≥ 1 requête représentative.

| # | query | discipline | mode_attendu | resultats_attendus | commentaire |
|---|---|---|---|---|---|
| C01 | | histoire | | | |
| C02 | | sociologie | | | |
| C03 | | philosophie | | | |
| C04 | | anthropologie | | | |
| C05 | | linguistique | | | |
| C06 | | litterature | | | |
| C07 | | droit | | | |
| C08 | | sciences-politiques | | | |
| C09 | | economie | | | |
| C10 | | geographie | | | |
| C11 | | psychologie | | | |
| C12 | | sciences-education | | | |
| C13 | | arts | | | |
| C14 | | medias-communication | | | |
| C15 | | informatique | | | |

### Bloc D — Requêtes par plateforme et type de document

| # | query | platformID | type | mode_attendu | resultats_attendus | commentaire |
|---|---|---|---|---|---|---|
| D01 | | OJ | article | lexical | | Revue, article de recherche |
| D02 | | OB | livre | lexical | | Livre académique |
| D03 | | OB | chapitre | hybride | | Chapitre de livre |
| D04 | | HO | post | hybride | | Billet de blog Hypothèses |
| D05 | | CO | evenement | lexical | | Événement Calenda |
| D06 | | OJ | compterendu | lexical | | Compte rendu de lecture |
| D07 | | | | | | |
| D08 | | | | | | |
| D09 | | | | | | |
| D10 | | | | | | |

### Bloc E — Cas limites et régressions

| # | query | cas | mode_attendu | resultats_attendus | resultats_absents | commentaire |
|---|---|---|---|---|---|---|
| E01 | | Requête vide / espace | lexical | — | — | Doit retourner résultats par défaut ou erreur 422 |
| E02 | | Requête très longue (>200 chars) | hybride | | | Tester la limite |
| E03 | | Caractères spéciaux | lexical | | | Apostrophes, tirets, guillemets |
| E04 | | Requête sans accent vs avec accent | lexical | | | "education" vs "éducation" |
| E05 | | Auteur connu | lexical | | | Doit remonter ses articles |
| E06 | | Titre exact entre guillemets | lexical | | | QB : titre exact |
| E07 | | Opérateur AND/OR/NOT | lexical | | | QB avancé |
| E08 | | Filtre + requête sémantique | hybride | | | Filtre plateforme + sens |
| E09 | | Requête avec chiffre/date | lexical | | | "révolution 1789" |
| E10 | | | | | | |

---

## Métriques cibles

Pour valider que la Phase 4 (recherche hybride) apporte de la valeur :

| Métrique | Cible | Mesure |
|---|---|---|
| MRR@10 (Mean Reciprocal Rank) | hybride ≥ lexical + 5% | Sur tous les blocs |
| NDCG@10 | hybride ≥ lexical + 5% | Sur Blocs B et C |
| Régression Bloc A | 0 régression | Les requêtes lexicales simples ne doivent pas régresser |
| Couverture discipline | ≥ 80% des requêtes C correctement classifiées | Post-Phase 3 |

---

## Procédure de validation

1. Remplir les 50 requêtes avec les équipes métier.
2. Lancer les requêtes contre l'API lexicale actuelle → scorer les résultats.
3. Après Phase 3 : lancer les mêmes requêtes en mode `hybrid` → comparer.
4. Si MRR et NDCG hybride ≥ lexical + 5% sur Blocs B/C sans régression Bloc A → Phase 4 validée pour production.
