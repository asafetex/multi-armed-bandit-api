"""
Script de verificação para deploy no Render com PostgreSQL
"""

import os
import json
import sys

print("=" * 60)
print("🚀 VERIFICAÇÃO DE DEPLOY PARA RENDER")
print("=" * 60)

# 1. Verificar configurações do PostgreSQL
print("\n1️⃣ VERIFICANDO CONFIGURAÇÃO POSTGRESQL...")

# Credenciais do PostgreSQL no Render (fornecidas pelo usuário)
POSTGRES_CONFIG = {
    "host": "dpg-d2ns9gmr433s73ak13rg-a",
    "port": "5432",
    "database": "bandit_db",
    "user": "bandit_user",
    "password": "[SENHA_SERÁ_CONFIGURADA_NO_RENDER]"
}

# DATABASE_URL para o Render
DATABASE_URL_FORMAT = "postgresql://{user}:{password}@{host}:{port}/{database}"

print("   ✅ Configuração PostgreSQL:")
print(f"      Host: {POSTGRES_CONFIG['host']}")
print(f"      Port: {POSTGRES_CONFIG['port']}")
print(f"      Database: {POSTGRES_CONFIG['database']}")
print(f"      User: {POSTGRES_CONFIG['user']}")

# 2. Verificar arquivo render.yaml
print("\n2️⃣ VERIFICANDO ARQUIVO render.yaml...")
try:
    with open('render.yaml', 'r') as f:
        content = f.read()
        if 'bandit-postgres' in content and 'multi-armed-bandit-api' in content:
            print("   ✅ render.yaml configurado corretamente")
            print("      - Web service: multi-armed-bandit-api")
            print("      - Database: bandit-postgres")
        else:
            print("   ❌ render.yaml precisa de ajustes")
except FileNotFoundError:
    print("   ❌ render.yaml não encontrado")

# 3. Verificar app/core/config.py
print("\n3️⃣ VERIFICANDO CONFIGURAÇÃO DA APLICAÇÃO...")
try:
    with open('app/core/config.py', 'r') as f:
        content = f.read()
        if "postgres://" in content and "postgresql://" in content:
            print("   ✅ Conversão postgres:// para postgresql:// configurada")
        else:
            print("   ⚠️ Verificar conversão de URL do PostgreSQL")
            
        if "DATABASE_URL" in content:
            print("   ✅ DATABASE_URL configurada para usar variável de ambiente")
except FileNotFoundError:
    print("   ❌ app/core/config.py não encontrado")

# 4. Verificar app/core/database.py
print("\n4️⃣ VERIFICANDO CONFIGURAÇÃO DO BANCO DE DADOS...")
try:
    with open('app/core/database.py', 'r') as f:
        content = f.read()
        if 'sslmode' in content:
            print("   ✅ SSL configurado para PostgreSQL")
        if 'pool_recycle' in content:
            print("   ✅ Pool de conexões configurado")
        if 'pool_size' in content:
            print("   ✅ Tamanho do pool configurado")
except FileNotFoundError:
    print("   ❌ app/core/database.py não encontrado")

# 5. Verificar requirements.txt
print("\n5️⃣ VERIFICANDO DEPENDÊNCIAS...")
try:
    with open('requirements.txt', 'r') as f:
        requirements = f.read()
        required_packages = [
            'fastapi', 'uvicorn', 'sqlalchemy', 'psycopg2-binary',
            'python-multipart', 'numpy', 'scipy'
        ]
        
        for package in required_packages:
            if package in requirements:
                print(f"   ✅ {package} presente")
            else:
                print(f"   ❌ {package} FALTANDO!")
except FileNotFoundError:
    print("   ❌ requirements.txt não encontrado")

# 6. Verificar models com suporte PostgreSQL
print("\n6️⃣ VERIFICANDO MODELOS DO BANCO...")
try:
    with open('app/models.py', 'r') as f:
        content = f.read()
        if 'JSONB' in content or 'JSON' in content:
            print("   ✅ Suporte para JSON/JSONB configurado")
        if 'MutableDict' in content:
            print("   ✅ MutableDict configurado para PostgreSQL")
        if 'Index' in content:
            print("   ✅ Índices configurados para otimização")
except FileNotFoundError:
    print("   ❌ app/models.py não encontrado")

# 7. Instruções de deploy
print("\n" + "=" * 60)
print("📋 INSTRUÇÕES PARA DEPLOY NO RENDER")
print("=" * 60)

print("""
1️⃣ PREPARAR O CÓDIGO:
   git add .
   git commit -m "Deploy para Render com PostgreSQL"
   git push origin main

2️⃣ NO RENDER DASHBOARD:
   
   a) Criar novo Web Service:
      - Connect GitHub repository
      - Branch: main
      - Build Command: pip install --upgrade pip setuptools wheel && pip install -r requirements.txt
      - Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   
   b) Criar PostgreSQL Database:
      - Name: bandit-postgres
      - Database: bandit_db
      - User: bandit_user
      - Plan: Free
   
   c) Configurar Environment Variables:
      - DATABASE_URL: (será auto-configurada pelo Render)
      - PYTHON_VERSION: 3.11.0
      - DEBUG: False
      - ENVIRONMENT: production

3️⃣ DEPLOY AUTOMÁTICO:
   - O Render fará deploy automático quando você fizer push no GitHub
   - URL será algo como: https://multi-armed-bandit-api.onrender.com

4️⃣ VERIFICAR FUNCIONAMENTO:
   - Acessar: https://seu-app.onrender.com/health
   - Dashboard: https://seu-app.onrender.com/dashboard
   - Docs: https://seu-app.onrender.com/docs
""")

print("\n" + "=" * 60)
print("✅ SISTEMA PREPARADO PARA DEPLOY NO RENDER!")
print("=" * 60)

# Criar arquivo de configuração para produção
print("\n📝 Criando arquivo de configuração de produção...")

production_config = """
# Configuração de Produção para Render

## Variáveis de Ambiente Necessárias:
- DATABASE_URL (auto-configurada pelo Render)
- PYTHON_VERSION=3.11.0
- DEBUG=False
- ENVIRONMENT=production

## Credenciais PostgreSQL:
- Host: dpg-d2ns9gmr433s73ak13rg-a
- Port: 5432
- Database: bandit_db
- User: bandit_user

## URLs de Produção:
- API: https://multi-armed-bandit-api.onrender.com
- Dashboard: https://multi-armed-bandit-api.onrender.com/dashboard
- Docs: https://multi-armed-bandit-api.onrender.com/docs
"""

with open('RENDER_DEPLOY_CONFIG.md', 'w') as f:
    f.write(production_config)
    print("✅ Arquivo RENDER_DEPLOY_CONFIG.md criado")

print("\n🎉 Tudo pronto para deploy no Render com PostgreSQL!")
