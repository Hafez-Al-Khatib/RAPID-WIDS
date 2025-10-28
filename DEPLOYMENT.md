# 🚀 RAPID Deployment Guide

Complete guide for deploying RAPID to various platforms.

## Table of Contents
- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Production Considerations](#production-considerations)

---

## Local Development

### Quick Start
```powershell
# Run setup script
.\setup.ps1

# Or manually:
docker-compose up -d
```

See [QUICKSTART.md](QUICKSTART.md) for detailed instructions.

---

## Docker Deployment

### Single Server Deployment

**Prerequisites:**
- Docker Engine 20.10+
- Docker Compose 1.29+
- 4GB RAM minimum
- 20GB disk space

**Steps:**

1. **Clone repository**
   ```bash
   git clone https://github.com/yourusername/RAPID-WIDS.git
   cd RAPID-WIDS
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with production values
   ```

3. **Build and start services**
   ```bash
   docker-compose up -d --build
   ```

4. **Initialize database**
   ```bash
   docker-compose exec backend python database.py
   ```

5. **Verify deployment**
   ```bash
   curl http://localhost:8000/
   ```

### Production Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  db:
    image: postgis/postgis:14-3.3
    restart: always
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - rapid-network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    restart: always
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@db:5432/${DB_NAME}
    depends_on:
      - db
    networks:
      - rapid-network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    restart: always
    depends_on:
      - backend
    networks:
      - rapid-network

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend
    networks:
      - rapid-network

volumes:
  postgres_data:

networks:
  rapid-network:
    driver: bridge
```

---

## Cloud Deployment

### AWS EC2

**1. Launch EC2 Instance**
- AMI: Ubuntu 22.04 LTS
- Instance Type: t3.medium (minimum)
- Security Group: Allow ports 22, 80, 443, 8000, 3000

**2. Install Docker**
```bash
sudo apt update
sudo apt install -y docker.io docker-compose
sudo usermod -aG docker ubuntu
```

**3. Clone and Deploy**
```bash
git clone https://github.com/yourusername/RAPID-WIDS.git
cd RAPID-WIDS
cp .env.example .env
# Edit .env
sudo docker-compose up -d
```

**4. Setup Domain (Optional)**
- Point domain to EC2 public IP
- Setup SSL with Let's Encrypt:
  ```bash
  sudo apt install certbot
  sudo certbot --nginx -d your-domain.com
  ```

### Google Cloud Platform (Cloud Run)

**1. Build containers**
```bash
# Backend
cd backend
gcloud builds submit --tag gcr.io/PROJECT-ID/rapid-backend

# Frontend
cd ../frontend
gcloud builds submit --tag gcr.io/PROJECT-ID/rapid-frontend
```

**2. Deploy to Cloud Run**
```bash
# Backend
gcloud run deploy rapid-backend \
  --image gcr.io/PROJECT-ID/rapid-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Frontend
gcloud run deploy rapid-frontend \
  --image gcr.io/PROJECT-ID/rapid-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

**3. Setup Cloud SQL**
```bash
gcloud sql instances create rapid-db \
  --database-version=POSTGRES_14 \
  --tier=db-f1-micro \
  --region=us-central1

# Enable PostGIS
gcloud sql databases create rapid_db --instance=rapid-db
```

### Azure Container Instances

**1. Create resource group**
```bash
az group create --name rapid-rg --location eastus
```

**2. Create container registry**
```bash
az acr create --resource-group rapid-rg --name rapidacr --sku Basic
```

**3. Build and push images**
```bash
az acr build --registry rapidacr --image rapid-backend ./backend
az acr build --registry rapidacr --image rapid-frontend ./frontend
```

**4. Deploy containers**
```bash
az container create \
  --resource-group rapid-rg \
  --name rapid-app \
  --image rapidacr.azurecr.io/rapid-backend \
  --dns-name-label rapid-app \
  --ports 8000
```

### Heroku

**1. Create apps**
```bash
heroku create rapid-backend
heroku create rapid-frontend
```

**2. Add PostgreSQL**
```bash
heroku addons:create heroku-postgresql:hobby-dev --app rapid-backend
```

**3. Deploy backend**
```bash
cd backend
git init
heroku git:remote -a rapid-backend
git add .
git commit -m "Deploy backend"
git push heroku main
```

**4. Deploy frontend**
```bash
cd ../frontend
# Add buildpack
heroku buildpacks:set heroku/nodejs --app rapid-frontend
git init
heroku git:remote -a rapid-frontend
git add .
git commit -m "Deploy frontend"
git push heroku main
```

---

## Production Considerations

### Security

**1. Environment Variables**
- Never commit `.env` files
- Use secrets management (AWS Secrets Manager, Azure Key Vault)
- Rotate credentials regularly

**2. Database**
- Enable SSL connections
- Use strong passwords
- Regular backups
- Restrict network access

**3. API Security**
- Enable CORS only for trusted domains
- Implement rate limiting
- Add authentication/authorization
- Use HTTPS only

**4. File Uploads**
- Validate file types
- Scan for malware
- Limit file sizes
- Use object storage (S3, GCS, Azure Blob)

### Performance

**1. Database Optimization**
```sql
-- Add indexes
CREATE INDEX idx_damage_reports_location ON damage_reports USING GIST(location);
CREATE INDEX idx_damage_reports_severity ON damage_reports(damage_severity);
CREATE INDEX idx_road_status_geometry ON road_status USING GIST(geometry);
```

**2. Caching**
- Redis for API responses
- CDN for frontend assets
- Cache OSM data locally

**3. Scaling**
- Horizontal scaling with load balancer
- Separate ML processing workers
- Database read replicas
- Auto-scaling groups

### Monitoring

**1. Application Monitoring**
- Logging: ELK stack, CloudWatch, Azure Monitor
- Metrics: Prometheus + Grafana
- APM: New Relic, Datadog, Application Insights

**2. Health Checks**
```python
# Add to main.py
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": check_db_connection(),
        "ml_models": check_models_loaded()
    }
```

**3. Alerts**
- High error rates
- Database connection failures
- High response times
- Disk space low

### Backup Strategy

**1. Database Backups**
```bash
# Automated daily backups
0 2 * * * pg_dump -h localhost -U postgres rapid_db > backup_$(date +\%Y\%m\%d).sql
```

**2. File Backups**
- Sync uploads directory to cloud storage
- Versioning enabled
- Cross-region replication

**3. Disaster Recovery**
- Document recovery procedures
- Test backups regularly
- Maintain off-site copies

### CI/CD Pipeline

**GitHub Actions Example:**

```yaml
name: Deploy RAPID

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          cd backend
          pip install -r requirements.txt
          pytest

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to production
        run: |
          # Your deployment commands
```

### Environment-Specific Configs

**Development:**
- Debug mode enabled
- Detailed error messages
- Hot reload
- Sample data

**Staging:**
- Production-like environment
- Realistic data volumes
- Performance testing
- Integration testing

**Production:**
- Debug mode disabled
- Error tracking
- Performance monitoring
- High availability

---

## Maintenance

### Regular Tasks

**Daily:**
- Monitor error logs
- Check system health
- Verify backups

**Weekly:**
- Review performance metrics
- Update dependencies
- Security scans

**Monthly:**
- Database optimization
- Cost analysis
- Capacity planning

### Updating RAPID

```bash
# Pull latest changes
git pull origin main

# Rebuild containers
docker-compose down
docker-compose up -d --build

# Run migrations (if any)
docker-compose exec backend alembic upgrade head
```

---

## Troubleshooting

### Common Issues

**Port conflicts:**
```bash
# Change ports in docker-compose.yml or .env
```

**Database connection errors:**
```bash
# Check database is running
docker-compose ps
# View logs
docker-compose logs db
```

**ML model download issues:**
```bash
# Pre-download models
docker-compose exec backend python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

**Out of memory:**
```bash
# Increase Docker memory limit
# Or upgrade instance size
```

---

## Support

For deployment issues:
1. Check logs: `docker-compose logs`
2. Review [QUICKSTART.md](QUICKSTART.md)
3. Open GitHub issue
4. Contact: your-email@example.com

---

## License

MIT License - See LICENSE file
