#!/bin/bash

# 🚀 Script de Deploy - Multi-Armed Bandit API
# Este script automatiza o processo de deploy no GitHub

set -e  # Exit on any error

echo "🎯 Multi-Armed Bandit API - Deploy Script"
echo "=========================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para print colorido
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar se Git está configurado
check_git_config() {
    print_status "Verificando configuração do Git..."
    
    if ! git config user.name > /dev/null; then
        print_error "Git user.name não configurado!"
        echo "Execute: git config --global user.name 'Seu Nome'"
        exit 1
    fi
    
    if ! git config user.email > /dev/null; then
        print_error "Git user.email não configurado!"
        echo "Execute: git config --global user.email 'seu.email@exemplo.com'"
        exit 1
    fi
    
    print_success "Git configurado corretamente"
}

# Verificar se Docker está funcionando
check_docker() {
    print_status "Verificando Docker..."
    
    if ! docker --version > /dev/null 2>&1; then
        print_error "Docker não encontrado! Instale o Docker primeiro."
        exit 1
    fi
    
    if ! docker compose version > /dev/null 2>&1; then
        print_error "Docker Compose não encontrado!"
        exit 1
    fi
    
    print_success "Docker OK"
}

# Testar aplicação localmente
test_application() {
    print_status "Testando aplicação localmente..."
    
    # Parar containers existentes
    docker compose down > /dev/null 2>&1 || true
    
    # Subir aplicação
    print_status "Iniciando containers..."
    docker compose up --build -d
    
    # Aguardar inicialização
    print_status "Aguardando inicialização (30s)..."
    sleep 30
    
    # Testar API
    if curl -f http://localhost:8000/ > /dev/null 2>&1; then
        print_success "API funcionando!"
    else
        print_error "API não está respondendo!"
        docker compose logs
        exit 1
    fi
    
    # Testar Dashboard
    if curl -f http://localhost:8000/dashboard > /dev/null 2>&1; then
        print_success "Dashboard funcionando!"
    else
        print_error "Dashboard não está respondendo!"
        exit 1
    fi
    
    print_success "Testes locais passaram!"
}

# Preparar repositório
prepare_repository() {
    print_status "Preparando repositório..."
    
    # Verificar se é um repositório Git
    if [ ! -d ".git" ]; then
        print_status "Inicializando repositório Git..."
        git init
        print_success "Repositório Git inicializado"
    fi
    
    # Verificar arquivos importantes
    required_files=("README.md" "LICENSE" ".gitignore" "requirements.txt" "docker-compose.yml")
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            print_error "Arquivo obrigatório não encontrado: $file"
            exit 1
        fi
    done
    
    print_success "Todos os arquivos obrigatórios presentes"
}

# Fazer commit e push
deploy_to_github() {
    print_status "Fazendo deploy para GitHub..."
    
    # Verificar se há mudanças
    if git diff --quiet && git diff --staged --quiet; then
        print_warning "Nenhuma mudança detectada"
        return
    fi
    
    # Adicionar arquivos
    print_status "Adicionando arquivos..."
    git add .
    
    # Verificar se remote origin existe
    if ! git remote get-url origin > /dev/null 2>&1; then
        print_error "Remote 'origin' não configurado!"
        echo "Configure com: git remote add origin https://github.com/SEU-USUARIO/multi-armed-bandit-api.git"
        exit 1
    fi
    
    # Commit
    commit_message="🚀 Deploy: Multi-Armed Bandit API

- ✅ FastAPI backend with PostgreSQL
- ✅ Thompson Sampling algorithm
- ✅ Interactive dashboard
- ✅ Docker containerization
- ✅ Complete documentation
- ✅ CI/CD pipeline

Deploy timestamp: $(date)"
    
    print_status "Fazendo commit..."
    git commit -m "$commit_message"
    
    # Push
    print_status "Enviando para GitHub..."
    git push -u origin main
    
    print_success "Deploy realizado com sucesso!"
}

# Criar release
create_release() {
    print_status "Criando release v1.0.0..."
    
    # Verificar se tag já existe
    if git tag -l | grep -q "v1.0.0"; then
        print_warning "Tag v1.0.0 já existe"
        return
    fi
    
    # Criar tag
    git tag -a v1.0.0 -m "🚀 Release v1.0.0: Production-ready Multi-Armed Bandit API

Features:
- Thompson Sampling algorithm implementation
- Interactive dashboard with real-time charts
- RESTful API with complete documentation
- Docker containerization for easy deployment
- CI/CD pipeline with automated testing
- Production-ready configuration

Technical Stack:
- FastAPI + PostgreSQL
- Chart.js for visualizations
- Docker + Docker Compose
- GitHub Actions for CI/CD"
    
    # Push tag
    git push origin v1.0.0
    
    print_success "Release v1.0.0 criada!"
    print_status "Acesse GitHub para criar a release page"
}

# Mostrar informações finais
show_final_info() {
    echo ""
    echo "🎉 Deploy Concluído com Sucesso!"
    echo "================================"
    echo ""
    echo "📋 Próximos passos:"
    echo "1. Acesse seu repositório no GitHub"
    echo "2. Configure GitHub Pages (Settings > Pages)"
    echo "3. Adicione topics ao repositório"
    echo "4. Crie a release page"
    echo "5. Adicione screenshots"
    echo ""
    echo "🔗 Links úteis:"
    echo "- Repositório: $(git remote get-url origin)"
    echo "- Dashboard local: http://localhost:8000/dashboard"
    echo "- API Docs: http://localhost:8000/docs"
    echo ""
    echo "📊 Para apresentação:"
    echo "- Mostre o dashboard funcionando"
    echo "- Demonstre a API no Swagger UI"
    echo "- Explique o algoritmo Thompson Sampling"
    echo "- Destaque a arquitetura e tecnologias"
    echo ""
    print_success "Boa sorte na apresentação! 🚀"
}

# Menu principal
main() {
    echo ""
    echo "Escolha uma opção:"
    echo "1) Deploy completo (recomendado)"
    echo "2) Apenas testar localmente"
    echo "3) Apenas fazer push para GitHub"
    echo "4) Criar release"
    echo "5) Sair"
    echo ""
    read -p "Opção [1-5]: " choice
    
    case $choice in
        1)
            check_git_config
            check_docker
            prepare_repository
            test_application
            deploy_to_github
            create_release
            show_final_info
            ;;
        2)
            check_docker
            test_application
            ;;
        3)
            check_git_config
            prepare_repository
            deploy_to_github
            ;;
        4)
            check_git_config
            create_release
            ;;
        5)
            print_status "Saindo..."
            exit 0
            ;;
        *)
            print_error "Opção inválida!"
            main
            ;;
    esac
}

# Executar menu principal
main
