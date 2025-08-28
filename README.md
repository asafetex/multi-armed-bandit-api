# Multi-Armed Bandit Optimization API

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/seu-usuario/multi-armed-bandit-api.svg)](https://github.com/seu-usuario/multi-armed-bandit-api/stargazers)

Uma API completa para otimização de testes A/B usando algoritmo Thompson Sampling, com dashboard interativo para análise de performance e alocação de tráfego.

> 🎯 **Otimize seus testes A/B automaticamente** - Deixe o algoritmo Thompson Sampling encontrar a melhor variante para você, minimizando o regret e maximizando conversões.

## 🎯 Visão Geral

Este projeto implementa uma solução robusta para otimização de testes A/B utilizando o algoritmo Multi-Armed Bandit (Thompson Sampling). A solução permite:

- **Alocação dinâmica de tráfego** baseada em performance em tempo real
- **Minimização de regret** através de exploração inteligente
- **Dashboard interativo** para visualização e análise de dados
- **API RESTful** para integração com sistemas existentes

## 🚀 Funcionalidades

### API Backend
- ✅ Criação e gerenciamento de experimentos A/B
- ✅ Coleta de métricas temporais (impressões, cliques, conversões)
- ✅ Algoritmo Thompson Sampling para alocação ótima
- ✅ Histórico de alocações e performance
- ✅ Endpoints para reset e limpeza de dados

### Dashboard Frontend
- ✅ Interface moderna e responsiva
- ✅ Gráficos interativos (CTR, Alocação, Regret, Confiança)
- ✅ Simulador de cenários
- ✅ Configurações avançadas do algoritmo
- ✅ Análise de performance em tempo real

## 🏗️ Arquitetura

```
├── app/
│   ├── main.py              # FastAPI application
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── crud.py              # Database operations
│   ├── database.py          # Database configuration
│   ├── config.py            # Application settings
│   └── services/
│       └── bandit.py        # Thompson Sampling algorithm
├── scripts/
│   ├── example_requests.py  # API usage examples
│   └── init.sql            # Database initialization
├── bandit-dashboard.html    # Interactive dashboard
├── docker-compose.yml      # Container orchestration
├── Dockerfile              # Application container
└── requirements.txt        # Python dependencies
```

## 🛠️ Tecnologias

**Backend:**
- **FastAPI** - Framework web moderno e performático
- **SQLAlchemy** - ORM para PostgreSQL
- **PostgreSQL** - Banco de dados relacional
- **Pydantic** - Validação de dados
- **NumPy** - Computação científica

**Frontend:**
- **HTML5/CSS3/JavaScript** - Interface moderna
- **Chart.js** - Visualizações interativas
- **Responsive Design** - Compatível com dispositivos móveis

**DevOps:**
- **Docker & Docker Compose** - Containerização
- **PostgreSQL** - Persistência de dados

## 🚀 Quick Start

### Pré-requisitos
- Docker e Docker Compose
- Git

### Instalação

1. **Clone o repositório:**
```bash
git clone https://github.com/asafetex/multi-armed-bandit-api.git
cd multi-armed-bandit-api
```

2. **Inicie os containers:**
```bash
docker compose up --build -d
```

3. **Acesse a aplicação:**
- **Dashboard:** http://localhost:8000/dashboard
- **API Docs:** http://localhost:8000/docs
- **API:** http://localhost:8000

## 📊 Como Usar

### 1. Criar um Experimento
```python
import requests

response = requests.post("http://localhost:8000/experiments", json={
    "name": "Homepage Button Test",
    "description": "Teste A/B do botão principal"
})
experiment_id = response.json()["id"]
```

### 2. Enviar Dados de Performance
```python
requests.post("http://localhost:8000/events", json={
    "experiment_id": experiment_id,
    "date": "2024-01-15",
    "variants": [
        {"variant_name": "control", "impressions": 10000, "clicks": 700},
        {"variant_name": "variant_b", "impressions": 10000, "clicks": 950}
    ]
})
```

### 3. Obter Alocação Ótima
```python
response = requests.get(f"http://localhost:8000/allocation?experiment_id={experiment_id}")
allocations = response.json()["allocations"]
# {"control": 0.25, "variant_b": 0.75}
```

## 🎮 Dashboard Interativo

O dashboard oferece uma interface completa para:

### Experimentos
- Criação de novos experimentos
- Envio de dados de performance
- Cálculo de alocações ótimas

### Análise
- **Performance CTR:** Evolução das taxas de conversão
- **Evolução da Alocação:** Como o algoritmo adapta o tráfego
- **Análise de Regret:** Custo de oportunidade acumulado
- **Intervalos de Confiança:** Significância estatística

### Simulação
- Teste de cenários hipotéticos
- Visualização de convergência do algoritmo
- Análise de performance comparativa

## 🧮 Algoritmo Thompson Sampling

O algoritmo implementado utiliza:

- **Distribuição Beta** para modelar incerteza
- **Exploração vs Exploração** balanceada
- **Alocação mínima** para controle (configurável)
- **Taxa de exploração** adaptativa
- **Convergência** para variante ótima

### Parâmetros Configuráveis
- `alpha_prior`: Prior da distribuição Beta (padrão: 1.0)
- `beta_prior`: Prior da distribuição Beta (padrão: 1.0)
- `min_explore_rate`: Taxa mínima de exploração (padrão: 5%)
- `control_floor`: Alocação mínima do controle (padrão: 10%)

## 📈 Métricas e KPIs

### Métricas Principais
- **CTR (Click-Through Rate):** Taxa de conversão por variante
- **Regret Acumulado:** Perda de oportunidade total
- **Taxa de Convergência:** Velocidade de otimização
- **Intervalo de Confiança:** Significância estatística

### Visualizações
- Gráficos de linha para evolução temporal
- Gráficos de barras para comparação
- Tabelas detalhadas com dados brutos
- Simulações interativas

## 🔧 Configuração Avançada

### Variáveis de Ambiente
```env
DATABASE_URL=postgresql://user:password@localhost/bandit_db
API_HOST=0.0.0.0
API_PORT=8000
```

### Personalização do Algoritmo
```python
# Em app/services/bandit.py
class ThompsonSampling:
    def __init__(self):
        self.alpha_prior = 1.0      # Ajustar para diferentes priors
        self.beta_prior = 1.0       # Ajustar para diferentes priors
        self.min_explore_rate = 0.05 # Taxa mínima de exploração
        self.control_floor = 0.10    # Piso do controle
```

## 🧪 Testes e Exemplos

Execute os exemplos de uso:
```bash
python scripts/example_requests.py
```

## 📚 API Reference

### Endpoints Principais

#### `POST /experiments`
Cria um novo experimento A/B.

#### `POST /events`
Envia dados de performance para um experimento.

#### `GET /allocation`
Calcula a alocação ótima usando Thompson Sampling.

#### `GET /experiments/{id}/history`
Obtém histórico de alocações de um experimento.

#### `POST /reset_data`
Limpa todos os dados (útil para desenvolvimento).

Documentação completa disponível em: http://localhost:8000/docs

## 🚀 Deploy em Produção

### Docker
```bash
# Build da imagem
docker build -t multi-armed-bandit-api .

# Deploy com compose
docker compose -f docker-compose.prod.yml up -d
```

### Kubernetes
```yaml
# Exemplo de deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bandit-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: bandit-api
  template:
    metadata:
      labels:
        app: bandit-api
    spec:
      containers:
      - name: api
        image: multi-armed-bandit-api:latest
        ports:
        - containerPort: 8000
```

## 🔒 Segurança

- Validação de entrada com Pydantic
- Sanitização de queries SQL
- Rate limiting (recomendado para produção)
- HTTPS (configurar reverse proxy)

## 📊 Monitoramento

Métricas recomendadas para produção:
- Latência de resposta da API
- Taxa de erro por endpoint
- Uso de CPU e memória
- Conexões de banco de dados
- Performance do algoritmo

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👥 Autor

**Seu Nome**
- GitHub: [@seu-usuario](https://github.com/asafetex)
- LinkedIn: [Seu Perfil](https://www.linkedin.com/in/asafeteixeira/)
- Email: asafetex@gmail.com

## 🙏 Agradecimentos

- Comunidade FastAPI pela excelente documentação
- Papers de pesquisa sobre Multi-Armed Bandits
- Comunidade open source

---

**⭐ Se este projeto foi útil, considere dar uma estrela no GitHub!**
