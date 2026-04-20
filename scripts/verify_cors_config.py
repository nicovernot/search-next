#!/usr/bin/env python3
"""
Script de vérification de la configuration CORS pour tous les environnements
"""
import os
import sys

# Ajouter le chemin de l'application
sys.path.insert(0, '/home/nico/projets/searchv2/search_api_solr')

def load_env_file(env_file):
    """Charge un fichier .env et retourne un dict"""
    config = {}
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
    return config

def check_cors_config(env_name, config):
    """Vérifie la configuration CORS d'un environnement"""
    print(f"\n{'='*70}")
    print(f"Environnement: {env_name.upper()}")
    print(f"{'='*70}")
    
    cors_origins = config.get('CORS_ORIGINS', '')
    if cors_origins:
        origins_list = [o.strip() for o in cors_origins.split(',')]
        print(f"✓ CORS Origins configurées ({len(origins_list)}):")
        for origin in origins_list:
            # Vérifications spécifiques selon l'environnement
            if env_name == 'development':
                if origin.startswith('http://localhost') or origin.startswith('http://127.0.0.1') or origin.startswith('http://0.0.0.0'):
                    print(f"  ✓ {origin} [OK - Development]")
                else:
                    print(f"  ⚠ {origin} [ATTENTION - Devrait être HTTP localhost]")
            elif env_name in ['production', 'staging']:
                if origin.startswith('https://'):
                    print(f"  ✓ {origin} [OK - HTTPS]")
                else:
                    print(f"  ❌ {origin} [ERREUR - Devrait être HTTPS]")
            else:  # test
                print(f"  ✓ {origin}")
    else:
        print(f"❌ CORS_ORIGINS non défini")
    
    # Vérifier les méthodes
    methods = config.get('CORS_ALLOW_METHODS', '')
    print(f"\n✓ Méthodes HTTP: {methods}")
    
    # Vérifier les credentials
    credentials = config.get('CORS_ALLOW_CREDENTIALS', '')
    if env_name == 'test' and credentials == 'false':
        print(f"✓ Credentials: {credentials} [OK - Désactivé pour les tests]")
    elif credentials == 'true':
        print(f"✓ Credentials: {credentials}")
    
    # Vérifier max-age
    max_age = config.get('CORS_MAX_AGE', '')
    print(f"✓ Max-Age: {max_age}s", end="")
    if env_name == 'development' and int(max_age) == 86400:
        print(" [OK - 24h pour dev]")
    elif env_name in ['production', 'staging'] and int(max_age) == 3600:
        print(" [OK - 1h pour prod/staging]")
    elif env_name == 'test' and int(max_age) == 60:
        print(" [OK - 1min pour test]")
    else:
        print()
    
    # Sécurité
    if env_name == 'production':
        https_redirect = config.get('ENABLE_HTTPS_REDIRECT', 'false')
        trusted_hosts = config.get('TRUSTED_HOSTS', '')
        print(f"\n🔒 Sécurité Production:")
        print(f"  ✓ HTTPS Redirect: {https_redirect}")
        print(f"  ✓ Trusted Hosts: {trusted_hosts}")

def main():
    """Fonction principale"""
    print("="*70)
    print("VÉRIFICATION DE LA CONFIGURATION CORS")
    print("="*70)
    
    base_path = '/home/nico/projets/searchv2/search_api_solr'
    environments = ['development', 'test', 'staging', 'production']
    
    all_ok = True
    
    for env_name in environments:
        env_file = f"{base_path}/.env.{env_name}"
        if not os.path.exists(env_file):
            print(f"\n❌ Fichier {env_file} non trouvé")
            all_ok = False
            continue
        
        config = load_env_file(env_file)
        check_cors_config(env_name, config)
    
    # Résumé
    print(f"\n{'='*70}")
    if all_ok:
        print("✅ Tous les fichiers de configuration sont présents")
    else:
        print("⚠️  Certains fichiers de configuration sont manquants")
    print(f"{'='*70}\n")

if __name__ == '__main__':
    main()
