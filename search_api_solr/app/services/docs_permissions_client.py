# app/services/docs_permissions_client.py
import re
from typing import Any
from urllib.parse import quote_plus, urlencode

import httpx

from app.core.logging import get_logger
from app.models import DocsPermissionsResponse, Organization
from app.settings import (
    FQ_IDS_ARE,
    FQ_SUBSCRIBERS_IS,
    FQ_TYPE_IS,
    SOLR_QUERY,
    settings,
)

logger = get_logger(__name__)

class SolrClient:
    """ Simulation d'un client Solr pour l'interface """
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def execute_solr_query(self, params: dict[str, Any]) -> dict[str, Any] | None:
        url = f"{self.base_url}/select?{urlencode(params, doseq=True)}"
        logger.info(f"Requête Solr exécutée: {url}")

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, timeout=10.0)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"Échec de la requête Solr: {e}")
                return None
            except Exception as e:
                logger.error(f"Erreur lors de l'accès à Solr: {e}")
                return None


class DocsPermissionsClient:

    RESPONSE_DEFAULT = {
        'data': {'organization': None, 'docs': None},
        'info': {},
    }

    def __init__(self, solr_client: SolrClient, settings: dict[str, Any]):
        self.settings = settings
        self.solr_client = solr_client

    def _escape_url_chars(self, value: str) -> str:
        """ Échappe les caractères spéciaux pour un filtre Solr """
        return re.sub(r'([+\-!(){}\[\]^"~*?:\\/|&])', r'\\\1', value)

    def _build_subscribers_filter_query(self, organization_shortname: str | None) -> str:
        """ Construit le filtre fq pour les abonnés et les types sans abonnement """

        types_needing_parents = self.settings.get('types_needing_parents', [])

        if not organization_shortname:
            logger.info("Organization shortname is empty, using only type filter")
            return FQ_TYPE_IS % (' OR '.join(types_needing_parents))

        where_subscribers_field_exists = FQ_SUBSCRIBERS_IS % organization_shortname
        where_subscribers_fields_is_missing = FQ_TYPE_IS % (' OR '.join(types_needing_parents))

        return f"{where_subscribers_field_exists} OR {where_subscribers_fields_is_missing}"

    def _create_solr_params(self, docs_urls: list[str], organization_shortname: str | None, fields: list[str] | None = None) -> dict[str, Any]:
        """ Construit le dictionnaire de paramètres Solr """

        # 1. Échapper les URLs et construire le FQ_IDS_ARE
        escaped_urls = [self._escape_url_chars(url) for url in docs_urls]
        fq_ids = FQ_IDS_ARE % (' OR '.join(escaped_urls))

        # 2. Construire le FQ d'abonnement
        fq_subscribers = self._build_subscribers_filter_query(organization_shortname)

        # 3. Champs à retourner (fl)
        fl_fields = fields if fields else self.settings.get('fl', [])

        params = {
            'q': SOLR_QUERY,
            'fq': [fq_ids, fq_subscribers],
            'fl': ' '.join(fl_fields),
            'rows': len(docs_urls),
            'wt': 'json'
        }
        return params

    def _extract_accessible_docs(self, response_docs: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """ Extrait les URLs et l'ID parent des documents de la réponse Solr """

        accessible_docs = []
        for doc in response_docs:
            accessible_docs.append({
                'url': doc.get('url'),
                'parent_id': doc.get('idparent'),
            })
        return accessible_docs

    @staticmethod
    def _formats_for_url(url: str, has_facsimile: bool) -> list[str]:
        """Dérive les formats disponibles selon la plateforme OpenEdition et la présence d'un PDF."""
        if 'journals.openedition.org' in url:
            # Revues : html + epub + pdf (accès institutionnel standard)
            return ['html', 'epub', 'pdf']
        if 'books.openedition.org' in url:
            return ['html', 'pdf'] if has_facsimile else ['html']
        # hypotheses.org, calenda.org, etc.
        return ['html']

    async def _fetch_doc_formats(self, docs_urls: list[str]) -> dict[str, list[str]]:
        """Dérive les formats disponibles par doc depuis Solr (files_facsimile) + type de plateforme."""
        escaped_urls = [self._escape_url_chars(url) for url in docs_urls]
        fq = FQ_IDS_ARE % (' OR '.join(escaped_urls))
        params = {'q': SOLR_QUERY, 'fq': fq, 'fl': 'url files_facsimile', 'rows': len(docs_urls), 'wt': 'json'}
        solr_response = await self.solr_client.execute_solr_query(params)

        # Index Solr results by URL
        solr_by_url: dict[str, bool] = {}
        if solr_response and solr_response.get('responseHeader', {}).get('status') == 0:
            for doc in solr_response['response']['docs']:
                url = doc.get('url')
                if url:
                    solr_by_url[url] = bool(doc.get('files_facsimile'))

        return {
            url: self._formats_for_url(url, solr_by_url.get(url, False))
            for url in docs_urls
        }

    async def _fetch_accessible_documents(self, organization: Organization, docs_urls: list[str]) -> list[dict[str, Any]]:
        """ Récupère les documents accessibles à l'organisation depuis Solr """

        params = self._create_solr_params(docs_urls, organization.shortname)
        solr_response = await self.solr_client.execute_solr_query(params)

        if not solr_response or solr_response['responseHeader']['status'] != 0:
            logger.error("Échec de la requête Solr initiale")
            return []

        response_docs = solr_response['response']['docs']
        return self._extract_accessible_docs(response_docs)

    def _format_response_docs(self, docs_urls: list[str], authorized_docs: Any, organization: Organization | None) -> list[dict[str, Any]]:
        """ Formate la réponse finale pour chaque URL demandée.
        authorized_docs peut être une liste de dicts {url,…} ou directement une liste d'URLs (str). """

        authorized_urls = [d if isinstance(d, str) else d['url'] for d in authorized_docs]
        formatted_docs = []

        org_formats = (organization.formats or []) if organization else []

        for url in docs_urls:
            is_permitted = url in authorized_urls

            # Si l'organisation a purchased = true, alors isPermitted = true
            if organization and organization.purchased:
                is_permitted = True
                logger.info(f"Document {url} autorisé via purchased=true")

            formatted_docs.append({
                'isPermitted': is_permitted,
                'url': url,
                'formats': org_formats if is_permitted else [],
            })
        return formatted_docs

    def _fill_up_response(self, organization: Organization | None = None, docs: list[dict[str, Any]] | None = None, info: dict[str, Any] | None = None) -> DocsPermissionsResponse:
        """ Construit l'objet de réponse final """

        response = self.RESPONSE_DEFAULT.copy()
        response['data']['organization'] = organization.dict() if organization else None
        response['data']['docs'] = docs
        if info:
            response['info'] = info

        return DocsPermissionsResponse(**response)

    async def _check_if_documents_have_parents(self, docs_urls: list[str], organization: Organization) -> dict[str, Any]:
        """ Vérifie si les documents demandés ont des parents et retourne l'info du premier parent trouvé """

        try:
            # On ne récupère que les champs nécessaires pour la vérification des parents
            fields = ['url', 'idparent', 'container_url']
            params = self._create_solr_params(docs_urls, organization.shortname, fields=fields)

            logger.info(f"Recherche de parents pour URLs: {docs_urls}")
            solr_response = await self.solr_client.execute_solr_query(params)

            if not solr_response or solr_response['responseHeader']['status'] != 0:
                logger.error("Échec de la vérification des parents")
                return {'parentId': None, 'parentUrl': None}

            response_docs = solr_response['response']['docs']

            for doc in response_docs:
                if doc.get('idparent'):
                    return {
                        'parentId': doc['idparent'],
                        'parentUrl': doc.get('container_url'),
                        'childUrl': doc.get('url')
                    }

            return {'parentId': None, 'parentUrl': None}

        except Exception as e:
            logger.error(f"Erreur lors de la vérification des parents: {e}")
            return {'parentId': None, 'parentUrl': None}

    async def _get_organization(self, remote_ip: str, docs_urls: list[str]) -> Organization | None:
        """ Appel l'API d'authentification pour obtenir les infos de l'organisation """

        # L'API auth identifie l'organisation par l'IP — une seule URL suffit comme contexte.
        # Passer plusieurs URLs (comma-join) supprime le champ `formats` de la réponse.
        first_url = quote_plus(docs_urls[0])
        url = f"{settings.auth_api_url}?ip={remote_ip}&url={first_url}"
        logger.info(f"Calling auth URL: {url}")

        async with httpx.AsyncClient() as client:
            try:
                # Utiliser follow_redirects=True pour gérer les codes 302
                response = await client.get(url, follow_redirects=True, timeout=10.0)

                # Le code PHP acceptait 200 et 302, httpx gère ça via follow_redirects
                if response.status_code not in [200]:
                    logger.error(f"Auth API returned non-success HTTP code: {response.status_code}")
                    return None

                user_data = response.json()
                logger.info(f"Parsed user data: {user_data}")

                # Si pas de username (shortname), on considère qu'il n'y a pas d'organisation (ex: freemium/anonyme)
                if not user_data.get('username'):
                    logger.info("No username found in auth response, returning None")
                    return None

                organization_data = {
                    'name': user_data.get('name'),
                    'shortname': user_data.get('username'),
                    'longname': user_data.get('long_name'),
                    'logoUrl': user_data.get('logo'),
                    'formats': user_data.get('formats'),
                    'purchased': bool(
                        user_data.get('oef_service_rights') or
                        user_data.get('oef_journals_rights')
                    ),
                }
                return Organization(**organization_data)

            except Exception as e:
                logger.error(f"Failed to get organization from auth API: {e}")
                return None


    async def handle_query(self, urls_str: str, remote_ip: str) -> DocsPermissionsResponse:
        """ Point d'entrée principal de la logique """

        logger.info(f"URLs received: {urls_str or 'null'}")
        logger.info(f"Remote IP: {remote_ip or 'null'}")

        if not remote_ip:
            logger.error("No remote IP, returning empty response")
            return self._fill_up_response()

        docs_urls = [url.strip() for url in urls_str.split(',') if url.strip()]
        if not docs_urls:
             logger.error("No URLs parsed, returning empty response")
             return self._fill_up_response()

        organization = await self._get_organization(remote_ip, docs_urls)

        if not organization:
            logger.error("No organization found, returning empty response")
            return self._fill_up_response()

        # Court-circuit : purchased=true → tous les docs sont accessibles
        if organization.purchased:
            logger.info(f"[purchased=true] {len(docs_urls)} docs autorisés directement")
            if organization.formats:
                # Auth a retourné les formats (cas journals) → même liste pour tous les docs
                formatted_docs = self._format_response_docs(docs_urls, docs_urls, organization)
            else:
                # Pas de formats auth (cas books) → une requête Solr pour files_facsimile
                doc_formats_map = await self._fetch_doc_formats(docs_urls)
                formatted_docs = []
                for url in docs_urls:
                    formatted_docs.append({
                        'isPermitted': True,
                        'url': url,
                        'formats': doc_formats_map.get(url, ['html']),
                    })
            return self._fill_up_response(organization, formatted_docs)

        # Sans purchased : vérifier si les documents ont des parents (logique abonnement Solr)
        parent_info = await self._check_if_documents_have_parents(docs_urls, organization)
        has_parent = parent_info['parentId'] is not None

        logger.info(f"Documents avec parents détectés: {'oui (ID: ' + parent_info['parentId'] + ')' if has_parent else 'non'}")

        effective_organization = organization
        if has_parent:
            parent_url = parent_info.get('parentUrl')
            if parent_url:
                logger.info(f"Récupération de l'organisation du parent: {parent_url}")
                parent_organization = await self._get_organization(remote_ip, [parent_url])
                if parent_organization:
                    if not parent_organization.formats and organization.formats:
                        parent_organization.formats = organization.formats
                    effective_organization = parent_organization
                    logger.info(f"Organisation du parent récupérée: {effective_organization.dict()}")

        return await self._fetch_permissions(effective_organization, docs_urls)

    async def _fetch_permissions(self, organization: Organization, docs_urls: list[str]) -> DocsPermissionsResponse:
        """ Récupère les documents accessibles et formate la réponse """

        documents_accessibles = await self._fetch_accessible_documents(organization, docs_urls)

        if not documents_accessibles:
            logger.error("Aucun document accessible trouvé")
            formatted_docs = self._format_response_docs(docs_urls, [], organization)
            return self._fill_up_response(organization, formatted_docs)

        # Construire la réponse finale
        formatted_docs = self._format_response_docs(docs_urls, documents_accessibles, organization)

        return self._fill_up_response(organization, formatted_docs)
