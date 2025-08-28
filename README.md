# Multi-Armed Bandit Optimization API

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Deploy](https://img.shields.io/badge/Deploy-Render-46E3B7.svg)](https://render.com)

A complete API for A/B test optimization using Thompson Sampling algorithm, with an interactive dashboard for performance analysis and traffic allocation.

> 🎯 **Optimize your A/B tests automatically** - Let the Thompson Sampling algorithm find the best variant for you, minimizing regret and maximizing conversions.

## 🎯 Overview

This project implements a robust solution for A/B test optimization using the Multi-Armed Bandit algorithm (Thompson Sampling). The solution provides:

- **Dynamic traffic allocation** based on real-time performance
- **Regret minimization** through intelligent exploration
- **Interactive dashboard** for data visualization and analysis
- **RESTful API** for integration with existing systems
- **Production-ready deployment** on Render platform

## 🚀 Features

### API Backend
- ✅ A/B experiment creation and management
- ✅ Temporal metrics collection (impressions, clicks, conversions)
- ✅ Thompson Sampling algorithm for optimal allocation
- ✅ Allocation and performance history
- ✅ Data reset and cleanup endpoints
- ✅ Comprehensive health checks
- ✅ Production logging and monitoring

### Dashboard Frontend
- ✅ Modern and responsive interface
- ✅ Interactive charts (CTR, Allocation, Regret, Confidence)
- ✅ Scenario simulator
- ✅ Advanced algorithm settings
- ✅ Real-time performance analysis

### Production Features
- ✅ Database connection pooling
- ✅ Structured logging
- ✅ Health check endpoints
- ✅ Environment-based configuration
- ✅ Docker containerization
- ✅ Render deployment ready

## 🏗️ Architecture

```
├── app/
│   ├── main.py              # FastAPI application with health checks
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── crud.py              # Database operations
│   ├── core/
│   │   ├── database.py      # Database config with connection pooling
│   │   └── config.py        # Production-ready settings
│   └── services/
│       └── bandit.py        # Thompson Sampling algorithm
├── scripts/
│   ├── example_requests.py  # API usage examples
│   └── init.sql            # Database initialization
├── bandit-dashboard.html    # Interactive dashboard
├── docker-compose.yml      # Container orchestration
├── Dockerfile              # Production-ready container
├── render.yaml             # Render deployment config
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
├── RENDER_DEPLOY.md        # Deployment guide
└── DEPLOY_CHECKLIST.md     # Pre-deployment checklist
```

## 🛠️ Technologies

**Backend:**
- **FastAPI** - Modern, fast web framework
- **SQLAlchemy** - ORM with connection pooling
- **PostgreSQL** - Relational database
- **Pydantic** - Data validation
- **NumPy** - Scientific computing

**Frontend:**
- **HTML5/CSS3/JavaScript** - Modern interface
- **Chart.js** - Interactive visualizations
- **Responsive Design** - Mobile-friendly

**DevOps:**
- **Docker & Docker Compose** - Containerization
- **Render** - Cloud deployment platform
- **PostgreSQL** - Managed database

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Git

### Local Development

1. **Clone the repository:**
```bash
git clone https://github.com/asafetex/multi-armed-bandit-api.git
cd multi-armed-bandit-api
```

2. **Start the containers:**
```bash
docker compose up --build -d
```

3. **Access the application:**
- **Dashboard:** http://localhost:8000/dashboard
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
- **API:** http://localhost:8000

### Production Deployment on Render

1. **Fork this repository to your GitHub account**

2. **Deploy on Render:**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Select `multi-armed-bandit-api`
   - Click "Apply"

3. **Access your deployed application:**
   - **API:** `https://your-app-name.onrender.com`
   - **Dashboard:** `https://your-app-name.onrender.com/dashboard`
   - **API Docs:** `https://your-app-name.onrender.com/docs`
   - **Health Check:** `https://your-app-name.onrender.com/health`

For detailed deployment instructions, see [RENDER_DEPLOY.md](RENDER_DEPLOY.md).

## 📊 How to Use

### 1. Create an Experiment
```python
import requests

response = requests.post("http://localhost:8000/experiments", json={
    "name": "Homepage Button Test",
    "description": "A/B test for main button"
})
experiment_id = response.json()["id"]
```

### 2. Send Performance Data
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

### 3. Get Optimal Allocation
```python
response = requests.get(f"http://localhost:8000/allocation?experiment_id={experiment_id}")
allocations = response.json()["allocations"]
# {"control": 0.25, "variant_b": 0.75}
```

## 🎮 Interactive Dashboard

The dashboard provides a complete interface for:

### Experiments
- Create new experiments
- Send performance data
- Calculate optimal allocations

### Analysis
- **CTR Performance:** Conversion rate evolution
- **Allocation Evolution:** How the algorithm adapts traffic
- **Regret Analysis:** Accumulated opportunity cost
- **Confidence Intervals:** Statistical significance

### Simulation
- Test hypothetical scenarios
- Visualize algorithm convergence
- Comparative performance analysis

## 🧮 Thompson Sampling Algorithm

The implemented algorithm uses:

- **Beta Distribution** to model uncertainty
- **Exploration vs Exploitation** balance
- **Minimum allocation** for control (configurable)
- **Adaptive exploration rate**
- **Convergence** to optimal variant

### Configurable Parameters
- `alpha_prior`: Beta distribution prior (default: 1.0)
- `beta_prior`: Beta distribution prior (default: 1.0)
- `min_explore_rate`: Minimum exploration rate (default: 5%)
- `control_floor`: Minimum control allocation (default: 10%)

## 📈 Metrics and KPIs

### Key Metrics
- **CTR (Click-Through Rate):** Conversion rate per variant
- **Cumulative Regret:** Total opportunity loss
- **Convergence Rate:** Optimization speed
- **Confidence Interval:** Statistical significance

### Visualizations
- Line charts for temporal evolution
- Bar charts for comparison
- Detailed tables with raw data
- Interactive simulations

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@host:port/database

# Application Settings
DEBUG=False
ENVIRONMENT=production

# Algorithm Parameters
DEFAULT_WINDOW_DAYS=14
MIN_IMPRESSIONS_FOR_OPTIMIZATION=1000

# Thompson Sampling Parameters
ALPHA_PRIOR=1.0
BETA_PRIOR=1.0
MIN_EXPLORE_RATE=0.05
CONTROL_FLOOR=0.1
MAX_DAILY_SHIFT=0.2
```

### Algorithm Customization
```python
# In app/services/bandit.py
class ThompsonSampling:
    def __init__(self):
        self.alpha_prior = 1.0      # Adjust for different priors
        self.beta_prior = 1.0       # Adjust for different priors
        self.min_explore_rate = 0.05 # Minimum exploration rate
        self.control_floor = 0.10    # Control floor
```

## 🧪 Testing and Examples

Run usage examples:
```bash
python scripts/example_requests.py
```

## 📚 API Reference

### Main Endpoints

#### `GET /health`
Comprehensive health check with database connectivity test.

#### `POST /experiments`
Create a new A/B test experiment.

#### `POST /events`
Send performance data for an experiment.

#### `GET /allocation`
Calculate optimal allocation using Thompson Sampling.

#### `GET /experiments/{id}/history`
Get allocation history for an experiment.

#### `POST /reset_data`
Clear all data (useful for development).

Complete documentation available at: `/docs`

## 🚀 Production Deployment

### Render (Recommended)

This project is optimized for Render deployment:

1. **Automatic Configuration:** Uses `render.yaml` for seamless setup
2. **Database Integration:** Automatic PostgreSQL provisioning
3. **Environment Variables:** Pre-configured for production
4. **Health Checks:** Built-in monitoring endpoints
5. **Logging:** Structured logging for debugging

See [RENDER_DEPLOY.md](RENDER_DEPLOY.md) for complete instructions.

### Docker

```bash
# Build image
docker build -t multi-armed-bandit-api .

# Production deployment
docker compose -f docker-compose.prod.yml up -d
```

### Kubernetes

```yaml
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
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
```

## 🔒 Security

- Input validation with Pydantic
- SQL query sanitization
- Rate limiting (recommended for production)
- HTTPS (configure reverse proxy)
- Environment-based secrets management

## 📊 Monitoring

### Built-in Health Checks
- Database connectivity
- Application status
- Environment information

### Recommended Production Metrics
- API response latency
- Error rate per endpoint
- CPU and memory usage
- Database connections
- Algorithm performance

### Logging
Structured logging with configurable levels:
```python
2025-01-01 10:00:00 - app.main - INFO - Application started
2025-01-01 10:00:01 - app.main - INFO - Database connection established
2025-01-01 10:00:02 - app.main - INFO - Health check passed
```

## 🤝 Contributing

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## 👥 Author

**Asafe Teixeira**
- GitHub: [@asafetex](https://github.com/asafetex)
- LinkedIn: [Asafe Teixeira](https://www.linkedin.com/in/asafeteixeira/)
- Email: asafetex@gmail.com

## 🙏 Acknowledgments

- FastAPI community for excellent documentation
- Multi-Armed Bandit research papers
- Open source community
- Render platform for seamless deployment

## 📋 Deployment Checklist

Before deploying to production, ensure:

- ✅ All tests pass locally
- ✅ Environment variables configured
- ✅ Database migrations applied
- ✅ Health checks responding
- ✅ Logging configured
- ✅ Security settings reviewed

See [DEPLOY_CHECKLIST.md](DEPLOY_CHECKLIST.md) for complete verification.

---

**⭐ If this project was helpful, please consider giving it a star on GitHub!**

**🚀 Ready for production deployment on Render!**
