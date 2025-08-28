# 🚀 Script de Deploy - Multi-Armed Bandit API (PowerShell)
# Este script automatiza o processo de deploy no GitHub para Windows

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("full", "test", "push", "release")]
    [string]$Action = "menu"
)

# Configurações
$ErrorActionPreference = "Stop"

Write-Host "🎯 Multi-Armed Bandit API - Deploy Script" -ForegroundColor Blue
Write-Host "==========================================" -ForegroundColor Blue

# Funções de output colorido
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Verificar configuração do Git
function Test-GitConfig {
    Write-Status "Verificando configuração do Git..."
    
    try {
        $userName = git config user.name
        $userEmail = git config user.email
        
        if (-not $userName) {
            Write-Error "Git user.name não configurado!"
            Write-Host "Execute: git config --global user.name 'Seu Nome'"
            exit 1
        }
        
        if (-not $userEmail) {
            Write-Error "Git user.email não configurado!"
            Write-Host "Execute: git config --global user.email 'seu.email@exemplo.com'"
            exit 1
        }
        
        Write-Success "Git configurado corretamente"
    }
    catch {
        Write-Error "Erro ao verificar configuração do Git: $_"
        exit 1
    }
}

# Verificar Docker
function Test-Docker {
    Write-Status "Verificando Docker..."
    
    try {
        $dockerVersion = docker --version 2>$null
        if (-not $dockerVersion) {
            Write-Error "Docker não encontrado! Instale o Docker Desktop primeiro."
            exit 1
        }
        
        $composeVersion = docker compose version 2>$null
        if (-not $composeVersion) {
            Write-Error "Docker Compose não encontrado!"
            exit 1
        }
        
        Write-Success "Docker OK"
    }
    catch {
        Write-Error "Erro ao verificar Docker: $_"
        exit 1
    }
}

# Testar aplicação localmente
function Test-Application {
    Write-Status "Testando aplicação localmente..."
    
    try {
        # Parar containers existentes
        Write-Status "Parando containers existentes..."
        docker compose down 2>$null
        
        # Subir aplicação
        Write-Status "Iniciando containers..."
        docker compose up --build -d
        
        # Aguardar inicialização
        Write-Status "Aguardando inicialização (30s)..."
        Start-Sleep -Seconds 30
        
        # Testar API
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/" -TimeoutSec 10
            if ($response.StatusCode -eq 200) {
                Write-Success "API funcionando!"
            }
        }
        catch {
            Write-Error "API não está respondendo!"
            docker compose logs
            exit 1
        }
        
        # Testar Dashboard
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/dashboard" -TimeoutSec 10
            if ($response.StatusCode -eq 200) {
                Write-Success "Dashboard funcionando!"
            }
        }
        catch {
            Write-Error "Dashboard não está respondendo!"
            exit 1
        }
        
        Write-Success "Testes locais passaram!"
    }
    catch {
        Write-Error "Erro durante os testes: $_"
        exit 1
    }
}

# Preparar repositório
function Initialize-Repository {
    Write-Status "Preparando repositório..."
    
    # Verificar se é um repositório Git
    if (-not (Test-Path ".git")) {
        Write-Status "Inicializando repositório Git..."
        git init
        Write-Success "Repositório Git inicializado"
    }
    
    # Verificar arquivos importantes
    $requiredFiles = @("README.md", "LICENSE", ".gitignore", "requirements.txt", "docker-compose.yml")
    
    foreach ($file in $requiredFiles) {
        if (-not (Test-Path $file)) {
            Write-Error "Arquivo obrigatório não encontrado: $file"
            exit 1
        }
    }
    
    Write-Success "Todos os arquivos obrigatórios presentes"
}

# Deploy para GitHub
function Deploy-ToGitHub {
    Write-Status "Fazendo deploy para GitHub..."
    
    try {
        # Verificar se há mudanças
        $status = git status --porcelain
        if (-not $status) {
            Write-Warning "Nenhuma mudança detectada"
            return
        }
        
        # Adicionar arquivos
        Write-Status "Adicionando arquivos..."
        git add .
        
        # Verificar se remote origin existe
        try {
            $origin = git remote get-url origin 2>$null
            if (-not $origin) {
                Write-Error "Remote 'origin' não configurado!"
                Write-Host "Configure com: git remote add origin https://github.com/SEU-USUARIO/multi-armed-bandit-api.git"
                exit 1
            }
        }
        catch {
            Write-Error "Remote 'origin' não configurado!"
            Write-Host "Configure com: git remote add origin https://github.com/SEU-USUARIO/multi-armed-bandit-api.git"
            exit 1
        }
        
        # Commit
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        $commitMessage = @"
🚀 Deploy: Multi-Armed Bandit API

- ✅ FastAPI backend with PostgreSQL
- ✅ Thompson Sampling algorithm
- ✅ Interactive dashboard
- ✅ Docker containerization
- ✅ Complete documentation
- ✅ CI/CD pipeline

Deploy timestamp: $timestamp
"@
        
        Write-Status "Fazendo commit..."
        git commit -m $commitMessage
        
        # Push
        Write-Status "Enviando para GitHub..."
        git push -u origin main
        
        Write-Success "Deploy realizado com sucesso!"
    }
    catch {
        Write-Error "Erro durante o deploy: $_"
        exit 1
    }
}

# Criar release
function New-Release {
    Write-Status "Criando release v1.0.0..."
    
    try {
        # Verificar se tag já existe
        $existingTag = git tag -l "v1.0.0" 2>$null
        if ($existingTag) {
            Write-Warning "Tag v1.0.0 já existe"
            return
        }
        
        # Criar tag
        $releaseMessage = @"
🚀 Release v1.0.0: Production-ready Multi-Armed Bandit API

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
- GitHub Actions for CI/CD
"@
        
        git tag -a v1.0.0 -m $releaseMessage
        
        # Push tag
        git push origin v1.0.0
        
        Write-Success "Release v1.0.0 criada!"
        Write-Status "Acesse GitHub para criar a release page"
    }
    catch {
        Write-Error "Erro ao criar release: $_"
        exit 1
    }
}

# Mostrar informações finais
function Show-FinalInfo {
    Write-Host ""
    Write-Host "🎉 Deploy Concluído com Sucesso!" -ForegroundColor Green
    Write-Host "================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Próximos passos:"
    Write-Host "1. Acesse seu repositório no GitHub"
    Write-Host "2. Configure GitHub Pages (Settings > Pages)"
    Write-Host "3. Adicione topics ao repositório"
    Write-Host "4. Crie a release page"
    Write-Host "5. Adicione screenshots"
    Write-Host ""
    Write-Host "🔗 Links úteis:"
    try {
        $origin = git remote get-url origin
        Write-Host "- Repositório: $origin"
    }
    catch {
        Write-Host "- Repositório: Configure o remote origin"
    }
    Write-Host "- Dashboard local: http://localhost:8000/dashboard"
    Write-Host "- API Docs: http://localhost:8000/docs"
    Write-Host ""
    Write-Host "📊 Para apresentação:"
    Write-Host "- Mostre o dashboard funcionando"
    Write-Host "- Demonstre a API no Swagger UI"
    Write-Host "- Explique o algoritmo Thompson Sampling"
    Write-Host "- Destaque a arquitetura e tecnologias"
    Write-Host ""
    Write-Success "Boa sorte na apresentação! 🚀"
}

# Menu principal
function Show-Menu {
    Write-Host ""
    Write-Host "Escolha uma opção:"
    Write-Host "1) Deploy completo (recomendado)"
    Write-Host "2) Apenas testar localmente"
    Write-Host "3) Apenas fazer push para GitHub"
    Write-Host "4) Criar release"
    Write-Host "5) Sair"
    Write-Host ""
    
    $choice = Read-Host "Opção [1-5]"
    
    switch ($choice) {
        "1" {
            Test-GitConfig
            Test-Docker
            Initialize-Repository
            Test-Application
            Deploy-ToGitHub
            New-Release
            Show-FinalInfo
        }
        "2" {
            Test-Docker
            Test-Application
        }
        "3" {
            Test-GitConfig
            Initialize-Repository
            Deploy-ToGitHub
        }
        "4" {
            Test-GitConfig
            New-Release
        }
        "5" {
            Write-Status "Saindo..."
            exit 0
        }
        default {
            Write-Error "Opção inválida!"
            Show-Menu
        }
    }
}

# Executar baseado no parâmetro
switch ($Action) {
    "full" {
        Test-GitConfig
        Test-Docker
        Initialize-Repository
        Test-Application
        Deploy-ToGitHub
        New-Release
        Show-FinalInfo
    }
    "test" {
        Test-Docker
        Test-Application
    }
    "push" {
        Test-GitConfig
        Initialize-Repository
        Deploy-ToGitHub
    }
    "release" {
        Test-GitConfig
        New-Release
    }
    "menu" {
        Show-Menu
    }
}
