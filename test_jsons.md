# JSONs de Teste para Endpoints da API Multi-Armed Bandit

## 📋 Sequência Completa de Teste

### 1️⃣ CRIAR EXPERIMENTO
**POST /experiments/**

```json
{
  "name": "Teste A/B Landing Page",
  "description": "Comparação entre versão atual e nova landing page com CTA otimizado"
}
```

### 2️⃣ ENVIAR DADOS - DIA 1
**POST /events**

```json
{
  "experiment_id": 1,
  "date": "2025-08-28",
  "variants": [
    {
      "variant_name": "control",
      "impressions": 1000,
      "clicks": 85,
      "conversions": 12
    },
    {
      "variant_name": "treatment",
      "impressions": 1000,
      "clicks": 120,
      "conversions": 18
    }
  ]
}
```

### 3️⃣ ENVIAR DADOS - DIA 2
**POST /events**

```json
{
  "experiment_id": 1,
  "date": "2025-08-27",
  "variants": [
    {
      "variant_name": "control",
      "impressions": 950,
      "clicks": 75,
      "conversions": 10
    },
    {
      "variant_name": "treatment",
      "impressions": 1050,
      "clicks": 115,
      "conversions": 20
    }
  ]
}
```

### 4️⃣ ENVIAR DADOS - DIA 3
**POST /events**

```json
{
  "experiment_id": 1,
  "date": "2025-08-26",
  "variants": [
    {
      "variant_name": "control",
      "impressions": 1100,
      "clicks": 92,
      "conversions": 14
    },
    {
      "variant_name": "treatment",
      "impressions": 900,
      "clicks": 108,
      "conversions": 16
    }
  ]
}
```

### 5️⃣ ENVIAR DADOS - DIA 4
**POST /events**

```json
{
  "experiment_id": 1,
  "date": "2025-08-25",
  "variants": [
    {
      "variant_name": "control",
      "impressions": 1200,
      "clicks": 96,
      "conversions": 13
    },
    {
      "variant_name": "treatment",
      "impressions": 800,
      "clicks": 104,
      "conversions": 19
    }
  ]
}
```

### 6️⃣ ENVIAR DADOS - DIA 5
**POST /events**

```json
{
  "experiment_id": 1,
  "date": "2025-08-24",
  "variants": [
    {
      "variant_name": "control",
      "impressions": 1000,
      "clicks": 80,
      "conversions": 11
    },
    {
      "variant_name": "treatment",
      "impressions": 1000,
      "clicks": 125,
      "conversions": 22
    }
  ]
}
```

### 7️⃣ CALCULAR ALOCAÇÃO
**GET /allocation?experiment_id=1&window_days=14**

URL completa:
```
https://multi-armed-bandit-api.onrender.com/allocation?experiment_id=1&window_days=14
```

Sem body, apenas query parameters:
- `experiment_id=1`
- `window_days=14`

### 8️⃣ VER DETALHES DO EXPERIMENTO
**GET /experiments/1**

URL completa:
```
https://multi-armed-bandit-api.onrender.com/experiments/1
```

### 9️⃣ VER HISTÓRICO DE ALOCAÇÕES
**GET /experiments/1/history**

URL completa:
```
https://multi-armed-bandit-api.onrender.com/experiments/1/history
```

---

## 🚀 Comandos CURL Prontos para Copiar e Colar

### Criar Experimento:
```bash
curl -X POST https://multi-armed-bandit-api.onrender.com/experiments/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Teste A/B Landing Page","description":"Comparação entre versão atual e nova landing page com CTA otimizado"}'
```

### Enviar Dados Dia 1:
```bash
curl -X POST https://multi-armed-bandit-api.onrender.com/events \
  -H "Content-Type: application/json" \
  -d '{"experiment_id":1,"date":"2025-08-28","variants":[{"variant_name":"control","impressions":1000,"clicks":85,"conversions":12},{"variant_name":"treatment","impressions":1000,"clicks":120,"conversions":18}]}'
```

### Enviar Dados Dia 2:
```bash
curl -X POST https://multi-armed-bandit-api.onrender.com/events \
  -H "Content-Type: application/json" \
  -d '{"experiment_id":1,"date":"2025-08-27","variants":[{"variant_name":"control","impressions":950,"clicks":75,"conversions":10},{"variant_name":"treatment","impressions":1050,"clicks":115,"conversions":20}]}'
```

### Enviar Dados Dia 3:
```bash
curl -X POST https://multi-armed-bandit-api.onrender.com/events \
  -H "Content-Type: application/json" \
  -d '{"experiment_id":1,"date":"2025-08-26","variants":[{"variant_name":"control","impressions":1100,"clicks":92,"conversions":14},{"variant_name":"treatment","impressions":900,"clicks":108,"conversions":16}]}'
```

### Enviar Dados Dia 4:
```bash
curl -X POST https://multi-armed-bandit-api.onrender.com/events \
  -H "Content-Type: application/json" \
  -d '{"experiment_id":1,"date":"2025-08-25","variants":[{"variant_name":"control","impressions":1200,"clicks":96,"conversions":13},{"variant_name":"treatment","impressions":800,"clicks":104,"conversions":19}]}'
```

### Enviar Dados Dia 5:
```bash
curl -X POST https://multi-armed-bandit-api.onrender.com/events \
  -H "Content-Type: application/json" \
  -d '{"experiment_id":1,"date":"2025-08-24","variants":[{"variant_name":"control","impressions":1000,"clicks":80,"conversions":11},{"variant_name":"treatment","impressions":1000,"clicks":125,"conversions":22}]}'
```

### Calcular Alocação:
```bash
curl -X GET "https://multi-armed-bandit-api.onrender.com/allocation?experiment_id=1&window_days=14"
```

### Ver Experimento:
```bash
curl -X GET https://multi-armed-bandit-api.onrender.com/experiments/1
```

### Ver Histórico:
```bash
curl -X GET https://multi-armed-bandit-api.onrender.com/experiments/1/history
```

---

## 📊 Dados Resumidos para Teste

Após inserir todos os dados acima, você terá:

**Variante Control:**
- Total Impressões: 5,250
- Total Cliques: 428
- Total Conversões: 60
- CTR Médio: 8.15%
- Taxa de Conversão: 14.02%

**Variante Treatment:**
- Total Impressões: 4,750
- Total Cliques: 572
- Total Conversões: 95
- CTR Médio: 12.04%
- Taxa de Conversão: 16.61%

**Resultado Esperado da Alocação:**
- Treatment deve receber maior alocação (~60-70%)
- Control deve receber menor alocação (~30-40%)

Isso porque Treatment tem melhor performance em CTR e Conversão!
