# 🔧 DEPLOYMENT TROUBLESHOOTING GUIDE

## Common Issues and Solutions

---

## Connection Issues

### Issue: "Cannot connect to PostgreSQL database"

**Error Message:**
```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) could not connect to server
```

**Solutions:**

1. **Check connection string format**
   ```
   postgresql://username:password@host:5432/database_name
   ```

2. **Verify PostgreSQL is running**
   ```bash
   # Linux/Mac
   pg_isready -h localhost -p 5432
   
   # Windows
   psql -U postgres -d postgres -c "SELECT 1"
   ```

3. **Check credentials**
   ```bash
   psql -U <username> -d <database> -h <host> -p 5432
   ```

4. **Verify firewall rules**
   - Ensure port 5432 is open
   - Check security groups (AWS/GCP/Azure)
   - Verify network ACLs

5. **Check database exists**
   ```bash
   psql -U postgres -c "\l" | grep fake_review_db
   ```

---

### Issue: "Connection pool timeout"

**Error Message:**
```
QueuePool limit of size 20 overflow 10 reached
```

**Solutions:**

1. **Increase connection pool size** in `.env`:
   ```
   DATABASE_POOL_SIZE=30
   DATABASE_MAX_OVERFLOW=20
   ```

2. **Check for connection leaks**
   ```python
   # Add logging to database.py
   logger.info(f"Active connections: {engine.pool.checkedout()}")
   ```

3. **Restart application** to reset pool

4. **Monitor active connections**
   ```sql
   SELECT count(*) FROM pg_stat_activity;
   ```

---

## Docker Issues

### Issue: "Docker daemon is not running"

**Solutions:**

1. **Start Docker daemon**
   ```bash
   # Linux
   sudo systemctl start docker
   
   # Mac
   open /Applications/Docker.app
   
   # Windows
   docker -v  # If not running, launch Docker Desktop
   ```

2. **Check Docker status**
   ```bash
   docker ps
   docker-compose ps
   ```

---

### Issue: "Port 8000 already in use"

**Error Message:**
```
ERROR: for api  Cannot start service api: Bind for 0.0.0.0:8000 failed
```

**Solutions:**

1. **Find process using port**
   ```bash
   # Linux/Mac
   lsof -i :8000
   
   # Windows
   netstat -ano | findstr :8000
   ```

2. **Kill the process** or **use different port**
   ```bash
   # In .env or docker-compose.yml
   API_PORT=8001
   ```

3. **Check docker-compose.yml**
   ```yaml
   ports:
     - "8001:8000"  # Change to different port
   ```

---

### Issue: "Docker image build fails"

**Solutions:**

1. **Check Dockerfile syntax**
   ```bash
   docker build --no-cache -t fake-review-detector .
   ```

2. **Check available disk space**
   ```bash
   df -h  # Linux/Mac
   Get-Volume  # Windows
   ```

3. **Clear Docker cache and rebuild**
   ```bash
   docker-compose down
   docker system prune -a
   docker-compose build --no-cache
   ```

---

## API Issues

### Issue: "API returns 500 error"

**Steps to debug:**

1. **Check logs**
   ```bash
   docker-compose logs api
   # or
   tail -f logs/api.log
   ```

2. **Check database connectivity**
   ```bash
   docker-compose exec api python -c "from app.database import engine; engine.connect()"
   ```

3. **Verify all dependencies installed**
   ```bash
   pip list | grep -E "fastapi|sqlalchemy|sklearn"
   ```

4. **Test API health endpoint**
   ```bash
   curl http://localhost:8000/health
   ```

---

### Issue: "403 Forbidden - Authentication failed"

**Solutions:**

1. **Check JWT_SECRET_KEY** in `.env`
   ```
   # Must be same in all instances
   JWT_SECRET_KEY=<strong-random-key>
   ```

2. **Verify token is being sent**
   ```bash
   curl -H "Authorization: Bearer <token>" http://localhost:8000/api/reviews/list
   ```

3. **Check CORS configuration**
   ```
   CORS_ORIGINS=http://localhost:3000,http://localhost:8501
   ```

---

### Issue: "API slow response (>1 second)"

**Diagnosis:**

1. **Check database query performance**
   ```python
   # Enable query logging
   SHOW_SQL_QUERIES=True
   ```

2. **Check API logs for slow endpoints**
   ```bash
   grep "duration" logs/api.log | sort -k2 -rn | head -10
   ```

3. **Monitor system resources**
   ```bash
   docker stats
   # Watch CPU, memory, network I/O
   ```

**Solutions:**

1. **Optimize database queries**
   - Add indexes
   - Use EXPLAIN ANALYZE
   - Cache frequent queries

2. **Scale horizontally**
   ```bash
   docker-compose up -d --scale api=3
   ```

3. **Reduce batch size** for ML predictions
   ```
   NLP_BATCH_SIZE=16
   ```

---

## Database Issues

### Issue: "Migrations fail / Database table doesn't exist"

**Solutions:**

1. **Check if init_db.py ran**
   ```bash
   docker-compose exec api python scripts/init_db.py
   ```

2. **Verify all models are imported**
   ```bash
   docker-compose exec api python -c "from app.models import *; print('Models loaded')"
   ```

3. **Check database connection**
   ```bash
   docker-compose exec postgres psql -U postgres -c "\dt"
   ```

---

### Issue: "Out of disk space - database won't start"

**Solutions:**

1. **Check disk usage**
   ```bash
   df -h
   du -sh /var/lib/postgresql/  # If using host volume
   ```

2. **Clean old logs**
   ```bash
   rm -f logs/*.log.*
   ```

3. **Expand volume**
   ```bash
   # For docker volumes
   docker volume ls
   # Increase storage allocation
   ```

---

## Model/ML Issues

### Issue: "Model file not found"

**Error Message:**
```
FileNotFoundError: [Errno 2] No such file or directory: './models/ensemble_model.pkl'
```

**Solutions:**

1. **Train model before starting API**
   ```bash
   docker-compose exec api python scripts/train_model.py
   ```

2. **Check model path** in `.env`
   ```
   ML_MODEL_PATH=./models/ensemble_model.pkl
   ```

3. **Mount volume correctly** in docker-compose.yml
   ```yaml
   volumes:
     - ./models:/app/models
   ```

---

### Issue: "Out of memory during model inference"

**Solutions:**

1. **Reduce batch size**
   ```
   NLP_BATCH_SIZE=8
   ```

2. **Disable BERT** (if not needed)
   ```
   USE_BERT=False
   ```

3. **Increase container memory**
   ```yaml
   # docker-compose.yml
   api:
     mem_limit: 4g
   ```

---

### Issue: "Model predictions very slow"

**Solutions:**

1. **Use pre-trained model** (skip retraining)
   ```bash
   # Don't run train_model.py
   ```

2. **Enable caching**
   ```
   USE_REDIS=True
   REDIS_CACHE_TTL=3600
   ```

3. **Use quantized model**
   ```python
   # In classifier/__init__.py
   model_type = "quantized"
   ```

---

## Monitoring & Observability

### Issue: "No logs appearing"

**Solutions:**

1. **Check log level**
   ```
   LOG_LEVEL=DEBUG  # for development
   LOG_LEVEL=INFO   # for production
   ```

2. **Verify log path exists**
   ```bash
   mkdir -p logs/
   chmod 755 logs/
   ```

3. **Check container logs**
   ```bash
   docker-compose logs -f api
   ```

---

### Issue: "Metrics not collecting"

**Solutions:**

1. **Enable metrics**
   ```
   ENABLE_METRICS=True
   METRICS_PORT=9090
   ```

2. **Verify Prometheus endpoint**
   ```bash
   curl http://localhost:9090/metrics
   ```

---

## Backup & Recovery

### Issue: "Cannot restore from backup"

**Solutions:**

1. **Verify backup file exists**
   ```bash
   ls -lh /backups/db_*.sql
   ```

2. **Check PostgreSQL version match**
   ```bash
   pg_dump --version
   ```

3. **Restore with verbose output**
   ```bash
   pg_restore -v -d fake_review_db /backups/db_backup.sql
   ```

---

## Security Issues

### Issue: "Unauthorized access to API"

**Solutions:**

1. **Generate new JWT secret**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Update .env and restart**
   ```
   JWT_SECRET_KEY=<new-secret>
   ```

3. **Check CORS configuration**
   ```
   CORS_ORIGINS=https://yourdomain.com
   ```

---

### Issue: "SSL/TLS certificate error"

**Solutions:**

1. **Verify certificate validity**
   ```bash
   openssl x509 -in /path/to/cert.pem -text -noout
   ```

2. **Install certificate** in Docker
   ```dockerfile
   COPY certs/ca.pem /etc/ssl/certs/
   RUN update-ca-certificates
   ```

3. **Update connection string** for SSL
   ```
   DATABASE_URL=postgresql+psycopg2://user:pass@host/db?sslmode=require
   ```

---

## Performance Tuning

### Issue: "High CPU usage"

**Diagnosis:**

```bash
docker stats api
ps aux | sort -k3 -rn | head -5
```

**Solutions:**

1. **Reduce worker processes**
   ```
   API_WORKERS=2
   ```

2. **Enable request profiling**
   ```
   PROFILE_REQUESTS=True
   ```

3. **Optimize slow endpoints**
   - Add database indexes
   - Reduce data processing
   - Implement caching

---

### Issue: "High memory usage"

**Solutions:**

1. **Monitor memory growth**
   ```bash
   docker stats --no-stream api
   ```

2. **Check for memory leaks**
   ```python
   import tracemalloc
   tracemalloc.start()
   ```

3. **Restart periodically**
   ```bash
   # docker-compose.yml
   restart: on-failure:5
   ```

---

## Rollback Procedures

### Quick Rollback to Previous Version

```bash
# Save current version
docker tag fake-review-detector:latest fake-review-detector:backup

# Revert to previous
git checkout HEAD~1
docker-compose down
docker-compose build
docker-compose up -d

# Or use backup image
docker tag fake-review-detector:backup fake-review-detector:latest
docker-compose up -d
```

---

## Getting Help

### Useful Commands for Debugging

```bash
# View all logs
docker-compose logs

# Follow API logs
docker-compose logs -f api

# View specific container
docker-compose logs api | tail -100

# Check health
curl http://localhost:8000/health

# Test database
docker-compose exec api python -c "from app.database import SessionLocal; db = SessionLocal(); print('DB OK')"

# Check environment
docker-compose exec api env | grep API

# Interactive shell
docker-compose exec api /bin/bash

# System info
docker info
docker version
docker-compose version
```

---

## Support Contact Matrix

| Issue Type | Contact | Response Time |
|-----------|---------|---------------|
| Database | DBA Team | 30 min |
| Infrastructure | DevOps | 30 min |
| Application | Backend Team | 15 min |
| Security | Security Team | 10 min (critical) |
| Performance | Platform Team | 60 min |

---

## Escalation Path

1. **Level 1**: Check logs and run diagnostics
2. **Level 2**: Restart services and check health
3. **Level 3**: Review recent changes and rollback if needed
4. **Level 4**: Escalate to senior DevOps/Platform team
5. **Level 5**: Escalate to CTO/Infrastructure leadership

---

## Prevention Tips

✅ **Always have backups**
✅ **Monitor logs continuously**
✅ **Test changes in staging first**
✅ **Keep dependencies updated**
✅ **Run load tests before production**
✅ **Document all configuration changes**
✅ **Use version control for everything**
✅ **Monitor resource utilization**

---

**Last Updated**: October 27, 2025
**Next Review**: November 27, 2025
