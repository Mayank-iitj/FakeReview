# 🚀 PRODUCTION DEPLOYMENT CHECKLIST

## Pre-Deployment Requirements

### Environment Setup
- [ ] Python 3.9+ installed
- [ ] PostgreSQL server running
- [ ] Redis server running (optional, for caching)
- [ ] Virtual environment created: `python -m venv venv`
- [ ] Dependencies installed: `pip install -r requirements.txt`

### Configuration Files
- [ ] `.env` file created and configured
- [ ] `DATABASE_URL` set to production PostgreSQL
- [ ] `JWT_SECRET_KEY` set to strong random value
- [ ] `API_PORT` set to desired port (default: 8000)
- [ ] Email credentials configured (if notifications needed)
- [ ] AWS/GCP/Azure credentials configured (if cloud deployment)

### Database Setup
- [ ] PostgreSQL database created
- [ ] User and password set
- [ ] Database tables initialized: `python scripts/init_db.py`
- [ ] Database connection tested
- [ ] Backup strategy configured

### Security
- [ ] JWT secret key is random and strong (min 32 characters)
- [ ] Database password is strong
- [ ] CORS origins configured correctly
- [ ] API rate limiting enabled
- [ ] HTTPS/SSL certificates obtained
- [ ] Firewall rules configured
- [ ] Secrets not committed to git

### Monitoring & Logging
- [ ] Logging level set appropriately
- [ ] Log rotation configured
- [ ] Error tracking setup (e.g., Sentry)
- [ ] Monitoring alerts configured
- [ ] Health check endpoint accessible
- [ ] Performance metrics collection enabled

### Testing
- [ ] Unit tests passing: `pytest tests/`
- [ ] Load testing completed
- [ ] Security testing completed
- [ ] API endpoints tested with production data
- [ ] Database backup/restore tested
- [ ] Failover scenarios tested

---

## Deployment Options

### Option 1: Docker Deployment (Recommended)

#### Pre-Flight Checks
- [ ] Run deployment check: `./deploy-check.sh` (Linux/Mac) or `deploy-check.bat` (Windows)
- [ ] All checks passed ✅
- [ ] Docker installed: `docker --version`
- [ ] Docker Compose installed: `docker-compose --version`

#### Deployment Steps
```bash
# 1. Build images
docker-compose build

# 2. Start services
docker-compose up -d

# 3. Initialize database
docker-compose exec api python scripts/init_db.py

# 4. Train models (optional)
docker-compose exec api python scripts/train_model.py

# 5. Verify services
docker-compose ps
curl http://localhost:8000/health
```

#### Post-Deployment Verification
- [ ] API container running: `docker-compose logs api`
- [ ] Dashboard container running: `docker-compose logs dashboard`
- [ ] Database container running: `docker-compose logs postgres`
- [ ] Health check passing: `curl http://localhost:8000/health`
- [ ] API documentation accessible: `http://localhost:8000/docs`
- [ ] Dashboard accessible: `http://localhost:8501`

### Option 2: AWS Deployment

#### Prerequisites
- [ ] AWS account created
- [ ] AWS CLI installed and configured
- [ ] ECR repository created
- [ ] RDS PostgreSQL instance created
- [ ] ElastiCache Redis instance (optional)

#### Deployment Steps
```bash
# 1. Build and push Docker image
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
docker tag fake-review-detector:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/fake-review-detector:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/fake-review-detector:latest

# 2. Update task definition with new image
aws ecs update-service --cluster fake-review-detector --service fake-review-api --force-new-deployment

# 3. Verify deployment
aws ecs describe-services --cluster fake-review-detector --services fake-review-api
```

- [ ] ECR image pushed
- [ ] ECS task definition updated
- [ ] ECS service updated
- [ ] Load balancer health checks passing
- [ ] CloudWatch logs showing healthy startup
- [ ] API endpoints responding

### Option 3: Google Cloud Run Deployment

#### Prerequisites
- [ ] Google Cloud project created
- [ ] gcloud CLI installed and authenticated
- [ ] Cloud SQL PostgreSQL instance created

#### Deployment Steps
```bash
# 1. Build and push image
gcloud builds submit --tag gcr.io/<project>/fake-review-detector

# 2. Deploy to Cloud Run
gcloud run deploy fake-review-detector \
  --image gcr.io/<project>/fake-review-detector \
  --platform managed \
  --region us-central1 \
  --set-env-vars DATABASE_URL=<cloud-sql-connection-string>

# 3. Set up Cloud Scheduler for periodic tasks
gcloud scheduler jobs create pubsub model-retrain \
  --location us-central1 \
  --schedule "0 2 * * 0" \
  --topic model-training
```

- [ ] Cloud Build triggered
- [ ] Image built and pushed
- [ ] Cloud Run service deployed
- [ ] Environment variables set
- [ ] Cloud SQL connected
- [ ] Health checks passing

### Option 4: Azure Container Instances

#### Prerequisites
- [ ] Azure account created
- [ ] Azure CLI installed
- [ ] Container Registry created
- [ ] Azure Database for PostgreSQL created

#### Deployment Steps
```bash
# 1. Build and push image
az acr build --registry <registry-name> --image fake-review-detector:latest .

# 2. Deploy container instance
az container create \
  --resource-group <group> \
  --name fake-review-detector \
  --image <registry>.azurecr.io/fake-review-detector:latest \
  --environment-variables DATABASE_URL=<connection-string>

# 3. Verify deployment
az container show --resource-group <group> --name fake-review-detector
```

- [ ] Image built and pushed to ACR
- [ ] Container instance created
- [ ] Environment variables configured
- [ ] Network access configured
- [ ] Health checks passing

### Option 5: Heroku Deployment

#### Prerequisites
- [ ] Heroku account created
- [ ] Heroku CLI installed
- [ ] Heroku Postgres add-on provisioned

#### Deployment Steps
```bash
# 1. Create Heroku app
heroku create fake-review-detector

# 2. Add buildpacks
heroku buildpacks:add heroku/python

# 3. Add Postgres
heroku addons:create heroku-postgresql:standard-0

# 4. Deploy
git push heroku main

# 5. Initialize database
heroku run python scripts/init_db.py

# 6. Scale dynos
heroku ps:scale web=2 worker=1
```

- [ ] Heroku app created
- [ ] Git remote configured
- [ ] Postgres add-on provisioned
- [ ] Code pushed successfully
- [ ] Database initialized
- [ ] Dynos scaled appropriately

---

## Post-Deployment Tasks

### Immediate (First Hour)
- [ ] Verify all services running
- [ ] Check API health: `curl /health`
- [ ] Test authentication endpoints
- [ ] Monitor logs for errors
- [ ] Verify database connectivity
- [ ] Confirm backups working

### First Day
- [ ] Test all API endpoints with production data
- [ ] Verify admin dashboard functionality
- [ ] Check email notifications (if enabled)
- [ ] Monitor system performance
- [ ] Review error logs
- [ ] Confirm backup frequency

### First Week
- [ ] Review performance metrics
- [ ] Check resource utilization
- [ ] Test failover procedures
- [ ] Verify disaster recovery plan
- [ ] Review security logs
- [ ] Plan capacity for scaling

### Ongoing
- [ ] Daily health checks
- [ ] Weekly log reviews
- [ ] Monthly security audits
- [ ] Quarterly disaster recovery drills
- [ ] Quarterly dependency updates
- [ ] Regular model retraining

---

## Monitoring & Alerts

### Critical Metrics to Monitor
```
API Response Time       < 100ms (p99)
Database Response Time  < 50ms (p99)
Error Rate              < 0.1%
CPU Usage               < 80%
Memory Usage            < 80%
Disk Space              > 10% free
Database Connections    < 80% of max
ML Model Prediction     < 200ms
```

### Alert Thresholds
- API Response Time > 500ms → Critical Alert
- Error Rate > 1% → Critical Alert
- CPU Usage > 90% → Warning Alert
- Memory Usage > 90% → Warning Alert
- Database Connections > 90% of max → Warning Alert
- Disk Space < 5% free → Critical Alert

### Logging Configuration
```python
# Configure Loguru for production
logger.add(
    "logs/api_{time}.log",
    rotation="1 day",
    retention="30 days",
    level="INFO"
)

logger.add(
    "logs/errors_{time}.log",
    rotation="1 day",
    retention="90 days",
    level="ERROR"
)
```

---

## Scaling Strategy

### Vertical Scaling (Increase Resources)
- Increase CPU/memory for single instance
- Increase database connection pool
- Upgrade database instance size
- Increase cache size (Redis)

### Horizontal Scaling (Add Instances)
```bash
# Docker Compose - Scale API service
docker-compose up -d --scale api=3

# Kubernetes - Scale deployment
kubectl scale deployment fake-review-api --replicas=5

# AWS ECS - Update desired count
aws ecs update-service --cluster fake-review-detector --service fake-review-api --desired-count 5
```

### Load Balancing
- Configure load balancer (nginx, HAProxy, AWS ELB)
- Use round-robin for distribution
- Configure health checks
- Set appropriate timeouts

---

## Disaster Recovery

### Backup Strategy
- Daily database backups (automated)
- Weekly full backups to external storage
- Monthly backups to archive storage
- Test restore procedures monthly

### Backup Configuration
```bash
# PostgreSQL daily backup
0 2 * * * pg_dump -U postgres fake_review_db > /backups/db_$(date +%Y%m%d).sql

# Upload to S3 weekly
0 3 * * 0 aws s3 cp /backups/ s3://fake-review-backups/ --recursive
```

### Recovery Procedures
1. **Point-in-time Recovery**: Restore to specific timestamp
2. **Full Recovery**: Restore entire database from backup
3. **Partial Recovery**: Restore specific tables/data
4. **Failover**: Switch to standby instance

---

## Security Checklist

- [ ] HTTPS/SSL enabled
- [ ] API authentication (JWT) working
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] SQL injection prevention (ORM used)
- [ ] XSS prevention headers set
- [ ] CSRF protection enabled
- [ ] Security headers configured
- [ ] Secrets rotated regularly
- [ ] Firewall rules configured
- [ ] VPC network isolated
- [ ] Encryption in transit (TLS)
- [ ] Encryption at rest configured
- [ ] Access logs enabled
- [ ] Security scanning configured

---

## Performance Optimization

### Database Optimization
```sql
-- Add indexes for common queries
CREATE INDEX idx_review_platform ON reviews(platform);
CREATE INDEX idx_review_status ON reviews(status);
CREATE INDEX idx_flag_created_at ON flags(created_at);
CREATE INDEX idx_review_created_at ON reviews(created_at);

-- Enable query statistics
ANALYZE;
```

### API Optimization
- Enable gzip compression
- Configure caching headers
- Use database connection pooling
- Implement request rate limiting
- Cache frequently accessed data (Redis)

### Model Optimization
- Use quantized models for faster inference
- Implement model caching
- Batch predictions when possible
- Consider model distillation for smaller size

---

## Maintenance Windows

### Schedule Regular Maintenance
- Database maintenance: Weekly (2-3 AM UTC)
- Dependency updates: Monthly
- Security patches: As needed (immediate)
- Model retraining: Weekly
- Log cleanup: Weekly
- Backup verification: Monthly

### Communication Plan
- Notify users 24 hours before maintenance
- Use maintenance mode/status page
- Keep status updated during maintenance
- Post mortem after completion

---

## Rollback Procedures

### For Code Updates
```bash
# Docker - Rollback to previous image
docker-compose down
docker rmi fake-review-detector:latest
docker pull fake-review-detector:previous
docker-compose up -d
```

### For Database Migrations
```bash
# Restore from pre-migration backup
pg_restore -d fake_review_db /backups/db_premigration.sql
```

### Communication
- Post incident status update
- Explain what failed
- Describe rollback actions taken
- Provide timeline for full resolution

---

## Deployment Sign-Off

- [ ] **Pre-deployment checks**: All passed
- [ ] **Configuration verified**: By DevOps team
- [ ] **Backups tested**: Confirmed working
- [ ] **Monitoring configured**: All alerts active
- [ ] **Documentation updated**: Latest version
- [ ] **Team notified**: Deployment window communicated
- [ ] **Go/No-Go decision**: Approved for deployment

**Deployment Date/Time**: ________________
**Deployed By**: ________________
**Approved By**: ________________

---

## Post-Deployment Sign-Off

- [ ] **All services running**: Confirmed
- [ ] **Health checks passing**: All green
- [ ] **API endpoints responding**: Verified
- [ ] **Database operational**: Confirmed
- [ ] **Monitoring active**: All metrics flowing
- [ ] **Logs clean**: No critical errors
- [ ] **Performance acceptable**: Meeting SLAs
- [ ] **Deployment successful**: Ready for users

**Deployment Completed**: ________________
**Verified By**: ________________
**Time**: ________________

---

## Emergency Contact

**On-Call Engineer**: [Name & Phone]
**DevOps Lead**: [Name & Phone]
**System Owner**: [Name & Phone]
**Escalation**: [Process & Contact]

---

## Support Resources

- Documentation: See DEPLOYMENT.md
- Troubleshooting: See DEPLOYMENT.md#Troubleshooting
- Monitoring: See monitoring dashboard
- Logs: Available in `/logs/` directory
- Status Page: [URL]
- Communication: [Channel/Slack]

---

**Last Updated**: October 27, 2025
**Next Review**: November 27, 2025
