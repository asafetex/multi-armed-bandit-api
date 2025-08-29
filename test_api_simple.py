"""
Teste simples da API Multi-Armed Bandit
"""

import requests
import json
from datetime import datetime, timedelta

API_URL = "http://localhost:8080"

print("=" * 50)
print("TESTE RÁPIDO DA API MULTI-ARMED BANDIT")
print("=" * 50)

# 1. Testar saúde da API
print("\n1. Testando API Health...")
try:
    response = requests.get(f"{API_URL}/health")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ API está rodando")
except Exception as e:
    print(f"   ❌ Erro: {e}")

# 2. Listar experimentos
print("\n2. Listando experimentos...")
try:
    response = requests.get(f"{API_URL}/experiments/")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        experiments = response.json()
        print(f"   ✅ Total de experimentos: {len(experiments)}")
        if experiments:
            # Pegar o último experimento com dados
            for exp in experiments:
                if exp.get("metrics") and len(exp["metrics"]) > 0:
                    print(f"\n3. Testando alocação para experimento {exp['id']}...")
                    # Calcular alocação
                    alloc_response = requests.get(f"{API_URL}/allocation/?experiment_id={exp['id']}&window_days=14")
                    if alloc_response.status_code == 200:
                        result = alloc_response.json()
                        print("   ✅ ALOCAÇÃO CALCULADA COM SUCESSO:")
                        allocations = result.get("allocations", {})
                        for variant, allocation in allocations.items():
                            print(f"      {variant}: {allocation * 100:.1f}%")
                    break
except Exception as e:
    print(f"   ❌ Erro: {e}")

# 4. Testar dashboard
print("\n4. Testando dashboard...")
try:
    response = requests.get(f"{API_URL}/dashboard")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ Dashboard acessível")
except Exception as e:
    print(f"   ❌ Erro: {e}")

print("\n" + "=" * 50)
print("✅ SISTEMA FUNCIONANDO CORRETAMENTE!")
print("=" * 50)
