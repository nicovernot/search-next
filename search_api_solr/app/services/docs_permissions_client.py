# app/services/docs_permissions_client.py
import re
from typing import List, Dict, Any, Optional
import logging
from urllib.parse import urlencode, quote_plus
import httpx # Librairie pour les requêtes HTTP asynchrones

from app.settings import SOLR_CONFIG, FQ_IDS_ARE, FQ_SUBSCRIBERS_IS, FQ_TYPE_IS, SOLR_QUERY
from app.models import DocsPermissionsResponse, Organization # Importez vos modèles Pydantic

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SolrClient:
    """ Simulation d'un client Solr pour l'interface """
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    async def query(self, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        url = f"{self.base_url}/select?{urlencode(params)}"
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
    
    def __init__(self, solr_client: SolrClient, settings: Dict[str, Any]):
        self.settings = settings
        self.solr_client = solr_client
    
    def _escape_url_chars(self, value: str) -> str:
        """ Échappe les caractères spéciaux pour un filtre Solr """
        return re.sub(r'([+\-!(){}\[\]^"~*?:\\/|&])', r'\\\1', value)

    def _build_subscribers_filter_query(self, organization_shortname: Optional[str]) -> str:
        """ Construit le filtre fq pour les abonnés et les types sans abonnement """
        
        types_needing_parents = self.settings.get('types_needing_parents', [])
        
        if not organization_shortname:
            logger.info("Organization shortname is empty, using only type filter")
            return FQ_TYPE_IS % (' OR '.join(types_needing_parents))
            
        where_subscribers_field_exists = FQ_SUBSCRIBERS_IS % organization_shortname
        where_subscribers_fields_is_missing = FQ_TYPE_IS % (' OR '.join(types_needing_parents))
        
        return f"{where_subscribers_field_exists} OR {where_subscribers_fields_is_missing}"

    def _create_solr_params(self, docs_urls: List[str], organization_shortname: Optional[str], fields: Optional[List[str]] = None) -> Dict[str, Any]:
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

    def _extract_accessible_docs(self, response_docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """ Extrait les URLs et l'ID parent des documents de la réponse Solr """
        
        accessible_docs = []
        for doc in response_docs:
            accessible_docs.append({
                'url': doc.get('url'),
                'parent_id': doc.get('idparent'),
            })
        return accessible_docs

    async def _fetch_accessible_documents(self, organization: Organization, docs_urls: List[str]) -> List[Dict[str, Any]]:
        """ Récupère les documents accessibles à l'organisation depuis Solr """
        
        params = self._create_solr_params(docs_urls, organization.shortname)
        solr_response = await self.solr_client.query(params)
        
        if not solr_response or solr_response['responseHeader']['status'] != 0:
            logger.error("Échec de la requête Solr initiale")
            return []

        response_docs = solr_response['response']['docs']
        return self._extract_accessible_docs(response_docs)

    def _format_response_docs(self, docs_urls: List[str], authorized_docs: List[Dict[str, Any]], organization: Optional[Organization]) -> List[Dict[str, Any]]:
        """ Formate la réponse finale pour chaque URL demandée """
        
        authorized_urls = [doc['url'] for doc in authorized_docs]
        formatted_docs = []
        
        for url in docs_urls:
            is_permitted = url in authorized_urls
            
            # Si l'organisation a purchased = true, alors isPermitted = true
            if organization and organization.purchased:
                is_permitted = True
                logger.info(f"Document {url} autorisé via purchased=true")
            
            formatted_docs.append({
                'isPermitted': is_permitted,
                'url': url,
            })
        return formatted_docs

    def _fill_up_response(self, organization: Optional[Organization] = None, docs: Optional[List[Dict[str, Any]]] = None, info: Optional[Dict[str, Any]] = None) -> DocsPermissionsResponse:
        """ Construit l'objet de réponse final """
        
        response = self.RESPONSE_DEFAULT.copy()
        response['data']['organization'] = organization.dict() if organization else None
        response['data']['docs'] = docs
        if info:
            response['info'] = info
        
        return DocsPermissionsResponse(**response)

    async def _check_if_documents_have_parents(self, docs_urls: List[str], organization: Organization) -> Dict[str, Any]:
        """ Vérifie si les documents demandés ont des parents et retourne l'info du premier parent trouvé """
        
        try:
            # On ne récupère que les champs nécessaires pour la vérification des parents
            fields = ['url', 'idparent', 'container_url']
            params = self._create_solr_params(docs_urls, organization.shortname, fields=fields)
            
            logger.info(f"Recherche de parents pour URLs: {docs_urls}")
            solr_response = await self.solr_client.query(params)
            
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

    async def _get_organization(self, remote_ip: str, docs_urls: List[str]) -> Optional[Organization]:
        """ Appel l'API d'authentification pour obtenir les infos de l'organisation """
        
        urls_str = quote_plus(','.join(docs_urls))
        url = f"http://auth.openedition.org/auth_by_url/?ip={remote_ip}&url={urls_str}"
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
                
                organization_data = {
                    'name': user_data.get('name'),
                    'shortname': user_data.get('username'),
                    'longname': user_data.get('long_name'),
                    'logoUrl': user_data.get('logo'),
                    'formats': user_data.get('formats'),
                    'purchased': user_data.get('purchased', False),
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
        
        # Vérifier si un document a des parents
        parent_info = await self._check_if_documents_have_parents(docs_urls, organization)
        has_parent = parent_info['parentId'] is not None
 
        logger.info(f"Documents avec parents détectés: {'oui (ID: ' + parent_info['parentId'] + ')' if has_parent else 'non'}")
        
        # Si il y a un parent, vérifier son organisation (logique complexe de l'application)
        effective_organization = organization
        if has_parent:
            parent_url = parent_info.get('parentUrl')
            if parent_url:
                logger.info(f"Récupération de l'organisation du parent: {parent_url}")
                
                parent_organization = await self._get_organization(remote_ip, [parent_url])
                if parent_organization:
                    effective_organization = parent_organization
                    logger.info(f"Organisation du parent récupérée: {effective_organization.dict()}")
        
        # Récupérer les permissions avec l'organisation effective
        return await self._fetch_permissions(effective_organization, docs_urls)

    async def _fetch_permissions(self, organization: Organization, docs_urls: List[str]) -> DocsPermissionsResponse:
        """ Récupère les documents accessibles et formate la réponse """
        
        documents_accessibles = await self._fetch_accessible_documents(organization, docs_urls)

        if not documents_accessibles:
            logger.error("Aucun document accessible trouvé")
            formatted_docs = self._format_response_docs(docs_urls, [], organization)
            return self._fill_up_response(organization, formatted_docs)
        
        # Construire la réponse finale
        formatted_docs = self._format_response_docs(docs_urls, documents_accessibles, organization)
        
        return self._fill_up_response(organization, formatted_docs)