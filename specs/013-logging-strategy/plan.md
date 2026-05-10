# Technical Plan: Stratégie de logs applicatifs

## Objectif

Passer d'un logging partiellement structuré et hétérogène à une politique simple :

- backend homogène, structuré, sûr ;
- frontend sobre et encadré ;
- séparation claire entre diagnostic dev et exploitation prod.

## État — audit 2026-05-10

| Zone | État | Risque résiduel |
|---|---|---|
| Backend `core/logging.py` | ✅ Root logger configuré — propagation correcte vers tous les modules | Aucun |
| Backend `basicConfig` | ✅ Supprimé — plus aucun appel dans le code métier | Aucun |
| Backend services — données sensibles | ✅ URL Solr complète → DEBUG structuré (`base_url` + `params_count`) ; IP déjà masquée via `_mask_ip` | Aucun |
| Backend services — f-strings | ✅ Convertis en `extra={"context": ...}` dans `SuggestService`, `PermissionsService`, `docs_permissions_client.py` | Aucun |
| Frontend | ✅ Wrapper `logger.ts` en place + règle ESLint `no-console` ajoutée | Aucun |
| Exploitation | Différenciation dev/prod présente (`settings.log_level`, Docker) — non normée formellement | Faible |

## Stratégie

Traiter le sujet en 4 lots, du plus structurant au plus visible :

1. fiabiliser la configuration backend ;
2. assainir les logs sensibles et les niveaux ;
3. uniformiser le frontend ;
4. documenter et vérifier.

## Phases

### Phase 1 — Configuration backend centrale

Travail :

- revoir `search_api_solr/app/core/logging.py` ;
- garantir l'application du formatter et des handlers aux loggers de modules ;
- décider explicitement du comportement du root logger ;
- aligner les loggers `uvicorn`, `uvicorn.error`, `uvicorn.access` si nécessaire.

Sortie attendue :

- un seul comportement de sortie ;
- plus aucun doute sur le format réel des logs applicatifs.

### Phase 2 — Normalisation backend métier

Travail :

- remplacer `logging.basicConfig()` dans `docs_permissions_client.py` ;
- harmoniser `auth.py`, `ldap_service.py`, `oidc_service.py`, `env_validation.py` ;
- convertir les logs texte utiles en logs structurés ;
- éviter les doubles logs d'une même erreur.

Sortie attendue :

- convention unique de logging pour tous les modules backend.

### Phase 3 — Redaction et politique par environnement

Travail :

- supprimer ou tronquer IP, URL complètes, réponses auth et payloads inutiles ;
- limiter `DEBUG` au développement ;
- garder en prod des signaux compacts : statut, durée, compteurs, identifiants sûrs.

Sortie attendue :

- logs exploitables sans fuite évidente de données.

### Phase 4 — Frontend

Travail :

- conserver `front/app/lib/logger.ts` comme point d'entrée unique ;
- vérifier que les hooks/composants métier ne réintroduisent pas `console.*` direct ;
- définir/valider le comportement dev/prod ;
- éventuellement ajouter une règle lint pour interdire `console.*` hors exceptions.

Sortie attendue :

- plus de logs ad hoc dispersés dans les hooks/composants.

### Phase 5 — Documentation et vérification

Travail :

- documenter la stratégie ;
- ajouter une checklist de revue ;
- valider via recherche globale et tests/lint.

Vérifications proposées :

```bash
rg -n "basicConfig\\(|console\\.(log|error|warn|info|debug)" search_api_solr front
rg -n "getLogger\\(|get_logger\\(" search_api_solr/app
```

## Priorisation

| Priorité | Sujet | Pourquoi |
|---|---|---|
| P1 | Configuration backend centrale | Conditionne tout le reste |
| P1 | Redaction des logs sensibles | Impact prod / sécurité |
| P2 | Wrapper frontend | Important mais non bloquant pour l'API |
| P2 | Documentation / lint | Durabilise la convention |

## Risques et garde-fous

| Risque | Garde-fou |
|---|---|
| Changer le logging casse la lisibilité locale en dev | prévoir un format dev lisible ou JSON compact testé localement |
| Doubler les logs `uvicorn` et applicatifs | tester la propagation et les handlers avant généralisation |
| Perdre du diagnostic en masquant trop | remplacer les données brutes par des métadonnées utiles |
| Ajouter une règle lint trop agressive | démarrer en warning |

## Décisions opérationnelles

- ne pas créer de branche dédiée tant qu'on reste au stade audit/spec ;
- créer une branche `feature/013-logging-strategy` au démarrage de l'implémentation ;
- traiter backend avant frontend ;
- considérer ce lot comme transverse qualité + exploitation, pas comme simple nettoyage cosmétique.
