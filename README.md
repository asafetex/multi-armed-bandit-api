# Multi-Armed Bandit Optimization API

A RESTful API that implements Multi-Armed Bandit algorithms (Thompson Sampling and Upper Confidence Bound) for A/B testing optimization with SQL integration. The system processes temporal experiment data and returns optimal traffic allocation percentages for control and variant groups.

## 🚀 Live Demo

- **API**: https://multi-armed-bandit-api.onrender.com
- **Interactive Dashboard**: https://multi-armed-bandit-api.onrender.com/dashboard
- **API Documentation**: https://multi-armed-bandit-api.onrender.com/docs

## 📋 Features

- **Thompson Sampling Algorithm**: Bayesian approach for optimal traffic allocation
- **Upper Confidence Bound (UCB)**: Alternative algorithm for exploration-exploitation balance
- **Multi-Variant Support**: Handle A/B/n tests with multiple variants
- **Real-time Dashboard**: Interactive visualization of experiment performance
- **SQL Integration**: PostgreSQL database for data persistence and analysis
- **RESTful API**: Clean endpoints for experiment management
- **Statistical Analysis**: Confidence intervals, conversion rates, and performance metrics

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python 3.11)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Algorithms**: NumPy, SciPy for statistical computations
- **Frontend**: HTML5, JavaScript, Chart.js for visualizations
- **Deployment**: Docker, Render.com

## 📊 API Endpoints

### Core Endpoints

- `POST /api/v1/experiments/` - Create new experiment
- `GET /api/v1/experiments/` - List all experiments
- `GET /api/v1/experiments/{experiment_id}` - Get experiment details
- `POST /api/v1/experiments/{experiment_id}/data` - Submit experiment data
- `GET /api/v1/experiments/{experiment_id}/allocation` - Get traffic allocation recommendations
- `GET /api/v1/experiments/{experiment_id}/statistics` - Get detailed statistics

### Dashboard

- `GET /dashboard` - Interactive experiment dashboard

## 🔧 Installation

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/asafetex/multi-armed-bandit-api.git
cd multi-armed-bandit-api
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

5. Run the application:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Deployment

```bash
docker-compose up -d
```

## 📝 Usage Example

### 1. Create an Experiment

```bash
curl -X POST "https://multi-armed-bandit-api.onrender.com/api/v1/experiments/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Homepage CTA Test",
    "description": "Testing different call-to-action buttons",
    "variants": ["Control", "Variant A", "Variant B"],
    "algorithm": "thompson_sampling"
  }'
```

### 2. Submit Experiment Data

```bash
curl -X POST "https://multi-armed-bandit-api.onrender.com/api/v1/experiments/1/data" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2025-01-28",
    "variant": "Control",
    "impressions": 1000,
    "conversions": 50
  }'
```

### 3. Get Traffic Allocation

```bash
curl "https://multi-armed-bandit-api.onrender.com/api/v1/experiments/1/allocation"
```

Response:
```json
{
  "allocations": {
    "Control": 25.5,
    "Variant A": 45.2,
    "Variant B": 29.3
  },
  "algorithm": "thompson_sampling",
  "confidence_level": 0.95
}
```

## 🗄️ Database Schema

```sql
-- Experiments table
CREATE TABLE experiments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    variants TEXT[],
    algorithm VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Experiment data table
CREATE TABLE experiment_data (
    id SERIAL PRIMARY KEY,
    experiment_id INTEGER REFERENCES experiments(id),
    date DATE NOT NULL,
    variant VARCHAR(100) NOT NULL,
    impressions INTEGER NOT NULL,
    conversions INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🧮 Algorithms

### Thompson Sampling
- Bayesian approach using Beta distributions
- Balances exploration and exploitation naturally
- Converges to optimal allocation over time

### Upper Confidence Bound (UCB)
- Deterministic algorithm with confidence intervals
- Provides theoretical guarantees on regret
- Suitable for scenarios requiring predictable behavior

## 📈 Performance Metrics

The API tracks and returns:
- **Conversion Rate (CTR)**: Conversions / Impressions
- **Confidence Intervals**: Statistical bounds on true conversion rate
- **Regret Minimization**: Optimal traffic allocation to maximize conversions
- **Sample Size**: Automatic calculation for statistical significance

## 🔐 Environment Variables

```env
DATABASE_URL=postgresql://user:password@localhost/bandit_db
API_V1_STR=/api/v1
PROJECT_NAME=Multi-Armed-Bandit-API
DEBUG=False
```

## 🧪 Testing

Run tests with pytest:
```bash
pytest tests/
```

## 📚 API Documentation

Interactive API documentation is available at:
- Swagger UI: https://multi-armed-bandit-api.onrender.com/docs
- ReDoc: https://multi-armed-bandit-api.onrender.com/redoc

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Author

**Asafe Teixeira**
- GitHub: [@asafetex](https://github.com/asafetex)

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- Render.com for hosting services
- Thompson Sampling and UCB algorithm research papers
- Open source community for continuous support

## 📞 Support

For issues and questions, please open an issue on GitHub or contact through the repository.

---

**Note**: This API is designed for production use in A/B testing scenarios. It handles real-time traffic allocation decisions based on statistical analysis of experiment data.
