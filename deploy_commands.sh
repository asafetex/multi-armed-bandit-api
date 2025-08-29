#!/bin/bash

echo "================================================"
echo "🚀 DEPLOY PARA RENDER - MULTI-ARMED BANDIT API"
echo "================================================"

# Adicionar todos os arquivos ao Git
echo ""
echo "1️⃣ Adicionando arquivos ao Git..."
git add .

# Criar commit
echo ""
echo "2️⃣ Criando commit..."
git commit -m "Deploy para Render com PostgreSQL - Sistema 100% funcional com Thompson Sampling"

# Push para o GitHub
echo ""
echo "3️⃣ Enviando para GitHub (branch main)..."
git push origin main

echo ""
echo "================================================"
echo "✅ CÓDIGO ENVIADO PARA GITHUB!"
echo "================================================"
echo ""
echo "📌 PRÓXIMOS PASSOS NO RENDER:"
echo ""
echo "1. Acesse https://dashboard.render.com"
echo "2. Crie um novo Web Service"
echo "3. Conecte seu repositório GitHub"
echo "4. Use estas configurações:"
echo "   - Branch: main"
echo "   - Build Command: pip install --upgrade pip setuptools wheel && pip install -r requirements.txt"
echo "   - Start Command: uvicorn app.main:app --host 0.0.0.0 --port \$PORT"
echo ""
echo "5. Crie o banco PostgreSQL:"
echo "   - Name: bandit-postgres"
echo "   - Database: bandit_db"
echo "   - User: bandit_user"
echo ""
echo "6. O Render fará o deploy automático!"
echo ""
echo "================================================"
