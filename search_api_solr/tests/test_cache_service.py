# tests/test_cache_service.py
"""
Tests pour le service de cache Redis
"""
from unittest.mock import AsyncMock, patch

import pytest

from app.models.logical_query import QueryGroup
from app.services.cache_service import CacheService


class TestCacheService:
    """Tests pour le service de cache Redis"""

    @pytest.fixture
    async def cache_service(self):
        """Fixture pour créer un service de cache de test"""
        # Utiliser des settings de test
        with patch('app.services.cache_service.settings') as mock_settings:
            mock_settings.redis_url = "redis://localhost:6379/1"  # DB de test
            mock_settings.redis_enabled = True
            mock_settings.redis_ttl_search = 60
            mock_settings.redis_ttl_suggest = 120
            mock_settings.redis_ttl_permissions = 90

            service = CacheService()
            yield service

            # Nettoyage
            if service.redis:
                await service.disconnect()

    @pytest.fixture
    async def mock_redis(self):
        """Fixture pour mocker Redis"""
        with patch('app.services.cache_service.Redis.from_url') as mock_from_url:
            mock_redis = AsyncMock()
            mock_from_url.return_value = mock_redis
            yield mock_redis

    def test_cache_service_initialization(self):
        """Test l'initialisation du service de cache"""
        service = CacheService()
        assert service.redis is None
        assert service.enabled is True  # Par défaut

    async def test_connect_success(self):
        """Test la connexion réussie à Redis"""
        with patch('app.services.cache_service.Redis.from_url') as mock_from_url:
            mock_redis = AsyncMock()
            # Configurer ping comme une coroutine qui retourne "PONG"
            mock_redis.ping = AsyncMock(return_value="PONG")
            # from_url retourne le client Redis, puis ping vérifie la connexion
            mock_from_url.return_value = mock_redis

            service = CacheService()
            await service.connect()

            assert service.redis is not None
            assert service.enabled is True
            mock_redis.ping.assert_called_once()

    async def test_connect_failure(self, mock_redis):
        """Test l'échec de connexion à Redis"""
        mock_redis.ping.side_effect = Exception("Connection failed")

        service = CacheService()
        await service.connect()

        assert service.redis is None
        assert service.enabled is False

    async def test_generate_cache_key(self, cache_service):
        """Test la génération de clés de cache"""
        data = {"query": "test", "filters": [{"type": "article"}]}
        key = cache_service._generate_cache_key("search", data)

        assert key.startswith("search:")
        assert len(key) > len("search:")

        # La même donnée doit générer la même clé
        key2 = cache_service._generate_cache_key("search", data)
        assert key == key2

        # Des données différentes doivent générer des clés différentes
        data2 = {"query": "test2", "filters": [{"type": "article"}]}
        key3 = cache_service._generate_cache_key("search", data2)
        assert key != key3

    async def test_generate_cache_key_with_logical_query_model(self, cache_service):
        """Test la génération de clé avec une recherche avancée Pydantic."""
        logical_query = QueryGroup(
            combinator="and",
            rules=[
                {"field": "titre", "operator": "contains", "value": "paris"},
                {"field": "titre", "operator": "contains", "value": "marseille"},
            ],
        )
        data = {
            "query": "science ouverte",
            "logical_query": logical_query,
            "filters": [],
        }

        key = cache_service._generate_cache_key("search", data)

        assert key.startswith("search:")

    async def test_get_cache_miss(self, cache_service, mock_redis):
        """Test récupération cache - miss"""
        mock_redis.get.return_value = None
        cache_service.redis = mock_redis

        result = await cache_service.get("test_key")

        assert result is None
        mock_redis.get.assert_called_once_with("test_key")

    async def test_get_cache_hit(self, cache_service, mock_redis):
        """Test récupération cache - hit"""
        cached_data = '{"result": "test_data"}'
        mock_redis.get.return_value = cached_data
        cache_service.redis = mock_redis

        result = await cache_service.get("test_key")

        assert result == {"result": "test_data"}
        mock_redis.get.assert_called_once_with("test_key")

    async def test_set_cache(self, cache_service, mock_redis):
        """Test stockage en cache"""
        cache_service.redis = mock_redis
        data = {"result": "test_data"}

        result = await cache_service.set("test_key", data, 300)

        assert result is True
        mock_redis.setex.assert_called_once_with("test_key", 300, '{"result": "test_data"}')

    async def test_delete_cache(self, cache_service, mock_redis):
        """Test suppression de cache"""
        mock_redis.delete.return_value = 1
        cache_service.redis = mock_redis

        result = await cache_service.delete("test_key")

        assert result is True
        mock_redis.delete.assert_called_once_with("test_key")

    async def test_clear_pattern(self, cache_service, mock_redis):
        """Test suppression par pattern"""
        mock_redis.keys.return_value = ["search:key1", "search:key2"]
        mock_redis.delete.return_value = 2
        cache_service.redis = mock_redis

        result = await cache_service.clear_pattern("search:*")

        assert result == 2
        mock_redis.keys.assert_called_once_with("search:*")
        mock_redis.delete.assert_called_once_with("search:key1", "search:key2")

    async def test_get_stats(self, cache_service, mock_redis):
        """Test récupération des statistiques"""
        mock_redis.info.return_value = {
            "connected_clients": 5,
            "used_memory_human": "1.2M",
            "keyspace_hits": 100,
            "keyspace_misses": 20
        }
        cache_service.redis = mock_redis

        stats = await cache_service.get_stats()

        assert stats["enabled"] is True
        assert stats["connected_clients"] == 5
        assert stats["used_memory"] == "1.2M"
        assert stats["keyspace_hits"] == 100
        assert stats["keyspace_misses"] == 20
        assert stats["hit_rate"] == 83.33  # 100/(100+20) * 100

    def test_calculate_hit_rate(self, cache_service):
        """Test calcul du taux de succès"""
        # Cas normal
        hit_rate = cache_service._calculate_hit_rate(80, 20)
        assert hit_rate == 80.0

        # Cas sans données
        hit_rate = cache_service._calculate_hit_rate(0, 0)
        assert hit_rate == 0.0

        # Cas avec seulement des misses
        hit_rate = cache_service._calculate_hit_rate(0, 100)
        assert hit_rate == 0.0

    async def test_search_cache_methods(self, cache_service, mock_redis):
        """Test les méthodes spécialisées pour le cache de recherche"""
        cache_service.redis = mock_redis

        # Test get_search_cache
        mock_redis.get.return_value = '{"results": "test"}'
        search_params = {"query": "test", "filters": []}

        result = await cache_service.get_search_cache(search_params)
        assert result == {"results": "test"}

        # Test set_search_cache
        mock_redis.setex.return_value = True
        results = {"response": {"docs": []}}

        success = await cache_service.set_search_cache(search_params, results)
        assert success is True

    async def test_suggest_cache_methods(self, cache_service, mock_redis):
        """Test les méthodes spécialisées pour le cache de suggestions"""
        cache_service.redis = mock_redis

        # Test get_suggest_cache
        mock_redis.get.return_value = '{"suggestions": ["test1", "test2"]}'

        result = await cache_service.get_suggest_cache("test")
        assert result == {"suggestions": ["test1", "test2"]}

        # Test set_suggest_cache
        mock_redis.setex.return_value = True
        suggestions = {"suggest": {"default": {"test": {"suggestions": ["test1"]}}}}

        success = await cache_service.set_suggest_cache("test", suggestions)
        assert success is True

    async def test_permissions_cache_methods(self, cache_service, mock_redis):
        """Test les méthodes spécialisées pour le cache de permissions"""
        cache_service.redis = mock_redis

        # Test get_permissions_cache
        mock_redis.get.return_value = '{"data": {"organization": "test"}}'

        result = await cache_service.get_permissions_cache("http://test.com", "192.168.1.1")
        assert result == {"data": {"organization": "test"}}

        # Test set_permissions_cache
        mock_redis.setex.return_value = True
        permissions = {"data": {"organization": "test", "docs": []}}

        success = await cache_service.set_permissions_cache("http://test.com", permissions, "192.168.1.1")
        assert success is True

    async def test_cache_disabled(self):
        """Test comportement quand le cache est désactivé"""
        with patch('app.services.cache_service.settings') as mock_settings:
            mock_settings.redis_enabled = False

            service = CacheService()

            # Toutes les opérations doivent retourner des valeurs par défaut
            assert await service.get("test") is None
            assert await service.set("test", {"data": "test"}, 300) is False
            assert await service.delete("test") is False
            assert await service.clear_pattern("*") == 0

            stats = await service.get_stats()
            assert stats == {"enabled": False}


class TestCacheIntegration:
    """Tests d'intégration pour le cache avec les services"""

    async def test_search_service_with_cache(self):
        """Test que SearchService utilise correctement le cache"""
        from unittest.mock import Mock

        from app.services.search_service import SearchService

        # Patcher le cache_service au bon endroit (import local dans la fonction)
        with patch('app.services.cache_service.cache_service') as mock_cache:
            mock_cache.get_search_cache = AsyncMock(return_value=None)
            mock_cache.set_search_cache = AsyncMock(return_value=True)

            # Mock des dépendances
            mock_builder = Mock()
            mock_builder.build_search_url.return_value = "http://solr/search?q=test"

            mock_solr_client = AsyncMock()
            mock_solr_client.search.return_value = {"response": {"docs": [], "numFound": 0}}

            service = SearchService(mock_builder, mock_solr_client)
            request = {"query": "test", "filters": [], "pagination": {"from": 0, "size": 10}}

            # Première recherche - pas de cache
            result = await service.execute_cached_search(request)

            # Vérifier que le cache a été consulté et mis à jour
            mock_cache.get_search_cache.assert_called_once_with(request)
            mock_cache.set_search_cache.assert_called_once()

            # Vérifier que Solr a été appelé
            mock_solr_client.search.assert_called_once()

            assert result == {'results': [], 'total': 0, 'facets': {}}

    async def test_search_service_cache_hit(self):
        """Test que SearchService retourne les résultats du cache quand disponibles"""
        from unittest.mock import Mock

        from app.services.search_service import SearchService

        # Configurer le cache pour retourner des données
        cached_result = {"results": [{"id": "1", "title": "Cached"}], "total": 1, "facets": {}}

        # Patcher le cache_service au bon endroit
        with patch('app.services.cache_service.cache_service') as mock_cache:
            mock_cache.get_search_cache = AsyncMock(return_value=cached_result)
            mock_cache.set_search_cache = AsyncMock(return_value=True)

            # Mock des dépendances
            mock_builder = Mock()
            mock_solr_client = AsyncMock()

            service = SearchService(mock_builder, mock_solr_client)
            request = {"query": "test", "filters": [], "pagination": {"from": 0, "size": 10}}

            # Recherche avec cache hit
            result = await service.execute_cached_search(request)

            # Vérifier que le cache a été consulté
            mock_cache.get_search_cache.assert_called_once_with(request)

            # Vérifier que Solr n'a PAS été appelé
            mock_solr_client.search.assert_not_called()

            # Vérifier que le cache n'a PAS été mis à jour
            mock_cache.set_search_cache.assert_not_called()

            assert result == cached_result
