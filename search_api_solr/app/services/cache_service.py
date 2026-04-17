# app/services/cache_service.py
import json
import hashlib
from typing import Any, Optional, Dict
from redis.asyncio import Redis
from app.core.logging import get_logger
from app.settings import settings

logger = get_logger(__name__)


class CacheService:
    """Service de cache Redis pour optimiser les performances"""
    
    def __init__(self):
        self.redis: Optional[Redis] = None
        self.enabled = settings.redis_enabled
        
    async def connect(self):
        """Établit la connexion à Redis"""
        if not self.enabled:
            logger.info("Redis cache disabled")
            return
            
        try:
            self.redis = Redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Test de connexion
            await self.redis.ping()
            logger.info(f"Redis cache connected successfully: {settings.redis_url}")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.enabled = False
            self.redis = None
    
    async def disconnect(self):
        """Ferme la connexion à Redis"""
        if self.redis:
            await self.redis.aclose()
            logger.info("Redis connection closed")
    
    def _generate_cache_key(self, prefix: str, data: Dict[str, Any]) -> str:
        """Génère une clé de cache unique basée sur les données"""
        # Sérialiser les données de manière déterministe
        serialized = json.dumps(
            self._make_json_safe(data),
            sort_keys=True,
            separators=(',', ':'),
            default=str,
        )
        # Créer un hash pour éviter les clés trop longues
        hash_key = hashlib.md5(serialized.encode()).hexdigest()
        return f"{prefix}:{hash_key}"

    def _make_json_safe(self, value: Any) -> Any:
        """Convertit les modèles Pydantic imbriqués avant sérialisation JSON."""
        if hasattr(value, "model_dump"):
            return self._make_json_safe(value.model_dump(by_alias=True))
        if isinstance(value, dict):
            return {key: self._make_json_safe(item) for key, item in value.items()}
        if isinstance(value, list):
            return [self._make_json_safe(item) for item in value]
        if isinstance(value, tuple):
            return tuple(self._make_json_safe(item) for item in value)
        return value
    
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Récupère une valeur du cache"""
        if not self.enabled or not self.redis:
            return None
            
        try:
            cached_data = await self.redis.get(key)
            if cached_data:
                logger.debug(f"Cache HIT for key: {key}")
                return json.loads(cached_data)
            else:
                logger.debug(f"Cache MISS for key: {key}")
                return None
                
        except Exception as e:
            logger.error(f"Redis GET error for key {key}: {e}")
            return None
    
    async def set(self, key: str, value: Dict[str, Any], ttl: int) -> bool:
        """Stocke une valeur dans le cache avec TTL"""
        if not self.enabled or not self.redis:
            return False
            
        try:
            serialized_value = json.dumps(value, ensure_ascii=False)
            await self.redis.setex(key, ttl, serialized_value)
            logger.debug(f"Cache SET for key: {key} (TTL: {ttl}s)")
            return True
            
        except Exception as e:
            logger.error(f"Redis SET error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Supprime une clé du cache"""
        if not self.enabled or not self.redis:
            return False
            
        try:
            result = await self.redis.delete(key)
            logger.debug(f"Cache DELETE for key: {key}")
            return result > 0
            
        except Exception as e:
            logger.error(f"Redis DELETE error for key {key}: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Supprime toutes les clés correspondant au pattern"""
        if not self.enabled or not self.redis:
            return 0
            
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                deleted = await self.redis.delete(*keys)
                logger.info(f"Cache CLEAR pattern {pattern}: {deleted} keys deleted")
                return deleted
            return 0
            
        except Exception as e:
            logger.error(f"Redis CLEAR pattern error for {pattern}: {e}")
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques du cache Redis"""
        if not self.enabled or not self.redis:
            return {"enabled": False}
            
        try:
            info = await self.redis.info()
            return {
                "enabled": True,
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "0B"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(
                    info.get("keyspace_hits", 0),
                    info.get("keyspace_misses", 0)
                )
            }
            
        except Exception as e:
            logger.error(f"Redis STATS error: {e}")
            return {"enabled": True, "error": str(e)}
    
    def _calculate_hit_rate(self, hits: int, misses: int) -> float:
        """Calcule le taux de succès du cache"""
        total = hits + misses
        if total == 0:
            return 0.0
        return round((hits / total) * 100, 2)
    
    # Méthodes spécialisées pour les différents types de cache
    
    async def get_search_cache(self, search_params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Récupère les résultats de recherche du cache"""
        key = self._generate_cache_key("search", search_params)
        return await self.get(key)
    
    async def set_search_cache(self, search_params: Dict[str, Any], results: Dict[str, Any]) -> bool:
        """Met en cache les résultats de recherche"""
        key = self._generate_cache_key("search", search_params)
        return await self.set(key, results, settings.redis_ttl_search)
    
    async def get_suggest_cache(self, query: str) -> Optional[Dict[str, Any]]:
        """Récupère les suggestions du cache"""
        key = self._generate_cache_key("suggest", {"query": query})
        return await self.get(key)
    
    async def set_suggest_cache(self, query: str, suggestions: Dict[str, Any]) -> bool:
        """Met en cache les suggestions"""
        key = self._generate_cache_key("suggest", {"query": query})
        return await self.set(key, suggestions, settings.redis_ttl_suggest)
    
    async def get_permissions_cache(self, urls: str, ip: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Récupère les permissions du cache"""
        cache_data = {"urls": urls}
        if ip:
            cache_data["ip"] = ip
        key = self._generate_cache_key("permissions", cache_data)
        return await self.get(key)
    
    async def set_permissions_cache(self, urls: str, permissions: Dict[str, Any], ip: Optional[str] = None) -> bool:
        """Met en cache les permissions"""
        cache_data = {"urls": urls}
        if ip:
            cache_data["ip"] = ip
        key = self._generate_cache_key("permissions", cache_data)
        return await self.set(key, permissions, settings.redis_ttl_permissions)


# Instance globale du service de cache
cache_service = CacheService()
