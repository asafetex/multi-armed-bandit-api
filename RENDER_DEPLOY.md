# 🚀 Deploy no Render - Multi-Armed Bandit API

Este guia fornece instruções passo a passo para fazer o deploy da API no Render.

## 📋 Pré-requisitos

- Conta no [Render](https://render.com)
- Repositório no GitHub com o código
- Arquivo `render.yaml` configurado (já incluído)

## 🔧 Passos para Deploy

### 1. Preparar o Repositório

Certifique-se de que todos os arquivos estão commitados:

```bash
git add .
git commit -m "feat: prepare for Render deployment"
git push origin main
```

### 2. Conectar ao Render

1. Acesse [Render Dashboard](https://dashboard.render.com)
2. Clique em "New +" → "Blueprint"
3. Conecte seu repositório GitHub
4. Selecione o repositório `multi-armed-bandit-api`

### 3. Configuração Automática

O Render detectará automaticamente o arquivo `render.yaml` e criará:

- **Web Service**: `multi-armed-bandit-api`
- **PostgreSQL Database**: `bandit-postgres`

### 4. Verificar Configurações

#### Web Service:
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Environment**: `python`
- **Python Version**: `3.11`

#### Database:
- **Name**: `bandit-postgres`
- **Database Name**: `bandit_db`
- **User**: `bandit_user`

### 5. Variáveis de Ambiente

As seguintes variáveis serão configuradas automaticamente:

- `DATABASE_URL`: Conectado automaticamente ao PostgreSQL
- `PYTHON_VERSION`: 3.11

Variáveis opcionais (podem ser adicionadas manualmente):
- `DEBUG=False`
- `ENVIRONMENT=production`

### 6. Deploy

1. Clique em "Apply" para iniciar o deploy
2. Aguarde o build completar (5-10 minutos)
3. O serviço estará disponível em: `https://multi-armed-bandit-api.onrender.com`

## 🔍 Verificação do Deploy

### Endpoints para Testar:

1. **Health Check**:
   ```
   GET https://multi-armed-bandit-api.onrender.com/health
   ```

2. **API Root**:
   ```
   GET https://multi-armed-bandit-api.onrender.com/
   ```

3. **Dashboard**:
   ```
   GET https://multi-armed-bandit-api.onrender.com/dashboard
   ```

4. **API Documentation**:
   ```
   GET https://multi-armed-bandit-api.onrender.com/docs
   ```

### Resposta Esperada do Health Check:

```json
{
  "status": "healthy",
  "database": "healthy",
  "version": "1.0.0",
  "environment": "production"
}
```

## 🐛 Troubleshooting

### Problema: Build Falha

**Solução**: Verificar logs de build no Render Dashboard

Possíveis causas:
- Dependências em `requirements.txt` incompatíveis
- Versão do Python incorreta

### Problema: Database Connection Error

**Solução**: 
1. Verificar se o PostgreSQL foi criado
2. Confirmar que `DATABASE_URL` está configurada
3. Aguardar alguns minutos para o banco inicializar

### Problema: Application Crash

**Solução**: Verificar logs da aplicação

Comandos úteis:
```bash
# Ver logs em tempo real
render logs --service multi-armed-bandit-api --tail

# Ver logs do banco
render logs --service bandit-postgres --tail
```

### Problema: Dashboard não Carrega

**Solução**: 
1. Verificar se `bandit-dashboard.html` foi incluído no build
2. Confirmar que o Dockerfile copia os arquivos HTML

## 📊 Monitoramento

### Métricas Disponíveis no Render:

- **CPU Usage**
- **Memory Usage**
- **Response Time**
- **Request Count**
- **Error Rate**

### Logs Importantes:

```bash
# Logs da aplicação
2025-01-01 10:00:00 - app.main - INFO - Application started
2025-01-01 10:00:01 - app.main - INFO - Database connection established

# Logs de health check
2025-01-01 10:00:02 - app.main - INFO - Health check passed
```

## 🔄 Atualizações

Para atualizar a aplicação:

1. Faça as alterações no código
2. Commit e push para o GitHub:
   ```bash
   git add .
   git commit -m "feat: update feature"
   git push origin main
   ```
3. O Render fará o redeploy automaticamente

## 🔒 Segurança

### Configurações Recomendadas:

1. **Environment Variables**: Nunca commitar credenciais
2. **HTTPS**: Habilitado automaticamente pelo Render
3. **Database**: Conexões criptografadas por padrão

### Variáveis Sensíveis:

- `DATABASE_URL`: Gerenciada automaticamente
- Adicionar outras credenciais via Render Dashboard

## 📈 Performance

### Otimizações Aplicadas:

1. **Connection Pooling**: Configurado no SQLAlchemy
2. **Logging**: Otimizado para produção
3. **CORS**: Configurado adequadamente
4. **Health Checks**: Endpoint dedicado

### Limites do Plano Free:

- **CPU**: Compartilhado
- **Memory**: 512MB
- **Database**: 1GB storage
- **Bandwidth**: 100GB/mês

## 🎯 URLs Finais

Após o deploy bem-sucedido:

- **API**: `https://multi-armed-bandit-api.onrender.com`
- **Dashboard**: `https://multi-armed-bandit-api.onrender.com/dashboard`
- **Docs**: `https://multi-armed-bandit-api.onrender.com/docs`
- **Health**: `https://multi-armed-bandit-api.onrender.com/health`

## 📞 Suporte

Em caso de problemas:

1. Verificar logs no Render Dashboard
2. Consultar [Render Documentation](https://render.com/docs)
3. Verificar status do serviço: [Render Status](https://status.render.com)

---

**✅ Deploy Concluído com Sucesso!**
