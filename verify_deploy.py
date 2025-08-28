#!/usr/bin/env python3
"""
Script para verificar se o deploy no Render está funcionando corretamente
"""

import requests
import json
import sys
from datetime import datetime

def test_endpoint(url, endpoint_name, expected_status=200):
    """Testa um endpoint e retorna o resultado"""
    try:
        print(f"🔍 Testando {endpoint_name}...")
        response = requests.get(url, timeout=10)
        
        if response.status_code == expected_status:
            print(f"✅ {endpoint_name}: OK ({response.status_code})")
            return True, response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        else:
            print(f"❌ {endpoint_name}: ERRO ({response.status_code})")
            return False, response.text
            
    except requests.exceptions.RequestException as e:
        print(f"❌ {endpoint_name}: ERRO DE CONEXÃO - {str(e)}")
        return False, str(e)

def main():
    if len(sys.argv) != 2:
        print("❌ Uso: python verify_deploy.py <URL_BASE>")
        print("📝 Exemplo: python verify_deploy.py https://multi-armed-bandit-api.onrender.com")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    
    print("🚀 Verificando deploy do Multi-Armed Bandit API")
    print(f"🌐 URL Base: {base_url}")
    print("=" * 60)
    
    # Lista de endpoints para testar
    endpoints = [
        ("/", "API Root"),
        ("/health", "Health Check"),
        ("/docs", "API Documentation"),
        ("/dashboard", "Dashboard")
    ]
    
    results = []
    
    for endpoint, name in endpoints:
        url = f"{base_url}{endpoint}"
        success, response = test_endpoint(url, name)
        results.append((name, success, response))
        print()
    
    # Resumo dos resultados
    print("=" * 60)
    print("📊 RESUMO DOS TESTES:")
    print("=" * 60)
    
    successful = 0
    total = len(results)
    
    for name, success, response in results:
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"{name}: {status}")
        if success:
            successful += 1
    
    print("=" * 60)
    print(f"🎯 RESULTADO FINAL: {successful}/{total} testes passaram")
    
    if successful == total:
        print("🎉 DEPLOY BEM-SUCEDIDO! Todos os endpoints estão funcionando.")
        print()
        print("🔗 URLs disponíveis:")
        print(f"   • Dashboard: {base_url}/dashboard")
        print(f"   • API Docs:  {base_url}/docs")
        print(f"   • Health:    {base_url}/health")
        print(f"   • API:       {base_url}/")
        
        # Teste específico do health check
        for name, success, response in results:
            if name == "Health Check" and success:
                print()
                print("🏥 DETALHES DO HEALTH CHECK:")
                try:
                    health_data = response
                    print(f"   • Status: {health_data.get('status', 'N/A')}")
                    print(f"   • Database: {health_data.get('database', 'N/A')}")
                    print(f"   • Version: {health_data.get('version', 'N/A')}")
                    print(f"   • Environment: {health_data.get('environment', 'N/A')}")
                except:
                    print("   • Dados do health check não puderam ser parseados")
        
        sys.exit(0)
    else:
        print("⚠️  ALGUNS TESTES FALHARAM. Verifique os logs do Render.")
        sys.exit(1)

if __name__ == "__main__":
    main()
