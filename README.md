# Multi-Armed Bandit Optimization API

API para otimização de testes A/B usando Thompson Sampling com integração SQL.

## Como Executar

```bash
# Com Docker
docker-compose up -d

# Testar
curl http://localhost:8000/health
```

## Endpoints

- **POST /events** - Enviar dados do experimento
- **GET /allocation** - Obter alocação otimizada

## Algoritmo

Thompson Sampling com:
- 5% exploração mínima
- 10% tráfego mínimo para controle
- 20% mudança máxima diária

## Tecnologias

- FastAPI
- PostgreSQL
- Docker
- Thompson Sampling (numpy/scipy)

---

## Testar se funciona

```bash
# 1. Parar tudo
docker-compose down -v

# 2. Reconstruir
docker-compose up --build -d

# 3. Aguardar 10 segundos

# 4. Testar novo endpoint /events
curl -X POST http://localhost:8000/events \
  -H "Content-Type: application/json" \
  -d '{
    "experiment_id": 1,
    "date": "2024-01-10", 
    "variants": [
      {"variant_name": "control", "impressions": 1000, "clicks": 70},
      {"variant_name": "variant_b", "impressions": 1000, "clicks": 95}
    ]
  }'

# 5. Testar novo endpoint /allocation
curl "http://localhost:8000/allocation?experiment_id=1"
```

---

## Subir no GitHub

```bash
# 1. Inicializar Git (se ainda não fez)
git init

# 2. Adicionar todos arquivos
git add .

# 3. Fazer commit
git commit -m "Multi-Armed Bandit API with Thompson Sampling"

# 4. Criar repositório no GitHub
# Vá em github.com, clique em "New Repository"
# Nome: bandit-api
# Deixe VAZIO (não crie README)
# Clique em "Create Repository"

# 5. Conectar ao GitHub (substitua SEU_USUARIO)
git remote add origin https://github.com/SEU_USUARIO/bandit-api.git

# 6. Enviar código
git branch -M main
git push -u origin main
```

---

## Verificação Final

- API funcionando?
  ```bash
  curl http://localhost:8000/
  ```
- Endpoints corretos?
  ```bash
  curl http://localhost:8000/events      # Deve dar erro 405 (precisa POST)
  curl http://localhost:8000/allocation  # Deve pedir experiment_id
  ```
- GitHub mostrando código?

Acesse: https://github.com/SEU_USUARIO/bandit-api

---

## Se der erro

**Erro de import?**
```bash
# No arquivo com erro, mude:
from .algo import Classe  # relativo
# Para:
from app.pasta.algo import Classe  # absoluto
```

**Erro no Docker?**
```bash
docker-compose logs api  # Ver o erro
docker-compose down -v   # Limpar tudo
docker-compose up --build  # Tentar de novo
```

**Erro no Git?**
```bash
git status  # Ver o que está acontecendo
git add .   # Adicionar tudo
git commit -m "fix: correções"
git push
