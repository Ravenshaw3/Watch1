# Deployment Guide

This guide covers deploying Watch1 Media Server to production environments.

## Production Checklist

Before deploying to production, ensure you have:

- [ ] Secure secret keys and passwords
- [ ] SSL certificates configured
- [ ] Database backups configured
- [ ] Monitoring and logging set up
- [ ] Firewall rules configured
- [ ] Resource limits defined
- [ ] Health checks implemented

## Deployment Options

### Option 1: Docker Compose (Recommended)

Best for single-server deployments with moderate traffic.

#### Prerequisites

- Docker and Docker Compose installed
- Domain name configured
- SSL certificates available
- Sufficient server resources (8GB+ RAM, 4+ CPU cores)

#### Production Configuration

1. **Create production environment file**
   ```bash
   cp env.example .env.production
   ```

2. **Update production settings**
   ```env
   # Production Environment
   ENVIRONMENT=production
   DEBUG=false
   SECRET_KEY=generate-secure-random-key-here
   
   # Database
   DATABASE_URL=postgresql://watch1:secure_password@postgres:5432/watch1_prod
   
   # Security
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   
   # SSL
   SSL_CERT_PATH=/etc/ssl/certs/watch1.crt
   SSL_KEY_PATH=/etc/ssl/private/watch1.key
   ```

3. **Update docker-compose.yml for production**
   ```yaml
   version: '3.8'
   
   services:
     postgres:
       environment:
         POSTGRES_DB: watch1_prod
         POSTGRES_USER: watch1
         POSTGRES_PASSWORD: ${DB_PASSWORD}
       volumes:
         - postgres_data:/var/lib/postgresql/data
         - ./backups:/backups
       restart: unless-stopped
   
     backend:
       environment:
         - ENVIRONMENT=production
         - DEBUG=false
         - SECRET_KEY=${SECRET_KEY}
       restart: unless-stopped
       deploy:
         resources:
           limits:
             memory: 2G
             cpus: '1.0'
   
     nginx:
       ports:
         - "80:80"
         - "443:443"
       volumes:
         - ./nginx/ssl:/etc/nginx/ssl
       restart: unless-stopped
   ```

4. **Deploy with production settings**
   ```bash
   docker-compose -f docker-compose.yml --env-file .env.production up -d
   ```

### Option 2: Kubernetes

Best for scalable, multi-server deployments.

#### Prerequisites

- Kubernetes cluster (1.20+)
- kubectl configured
- Helm (optional, for easier management)
- Persistent storage configured

#### Kubernetes Manifests

Create the following manifests:

**namespace.yaml**
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: watch1
```

**configmap.yaml**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: watch1-config
  namespace: watch1
data:
  DATABASE_URL: "postgresql://watch1:password@postgres:5432/watch1"
  REDIS_URL: "redis://redis:6379"
  ENVIRONMENT: "production"
```

**secret.yaml**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: watch1-secrets
  namespace: watch1
type: Opaque
data:
  SECRET_KEY: <base64-encoded-secret>
  DB_PASSWORD: <base64-encoded-password>
```

**deployment.yaml**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: watch1-backend
  namespace: watch1
spec:
  replicas: 3
  selector:
    matchLabels:
      app: watch1-backend
  template:
    metadata:
      labels:
        app: watch1-backend
    spec:
      containers:
      - name: backend
        image: watch1/backend:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: watch1-config
        - secretRef:
            name: watch1-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

**service.yaml**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: watch1-backend
  namespace: watch1
spec:
  selector:
    app: watch1-backend
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

**ingress.yaml**
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: watch1-ingress
  namespace: watch1
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - yourdomain.com
    secretName: watch1-tls
  rules:
  - host: yourdomain.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: watch1-backend
            port:
              number: 8000
      - path: /
        pathType: Prefix
        backend:
          service:
            name: watch1-frontend
            port:
              number: 3000
```

#### Deploy to Kubernetes

```bash
# Apply manifests
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f ingress.yaml

# Check deployment status
kubectl get pods -n watch1
kubectl get services -n watch1
kubectl get ingress -n watch1
```

### Option 3: Cloud Platforms

#### AWS ECS

1. **Create ECS cluster**
2. **Define task definitions**
3. **Set up Application Load Balancer**
4. **Configure RDS for database**
5. **Use ElastiCache for Redis**

#### Google Cloud Run

1. **Build and push container images**
2. **Deploy services to Cloud Run**
3. **Configure Cloud SQL for database**
4. **Set up Cloud Memorystore for Redis**
5. **Configure Cloud Load Balancing**

#### Azure Container Instances

1. **Create container groups**
2. **Configure Azure Database for PostgreSQL**
3. **Set up Azure Cache for Redis**
4. **Configure Application Gateway**

## SSL/TLS Configuration

### Let's Encrypt with Certbot

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Nginx SSL Configuration

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Rest of your configuration...
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

## Database Setup

### PostgreSQL Production Configuration

```sql
-- Create production database
CREATE DATABASE watch1_prod;
CREATE USER watch1 WITH ENCRYPTED PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE watch1_prod TO watch1;

-- Configure for production
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
```

### Database Backups

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
DB_NAME="watch1_prod"

# Create backup
pg_dump -h localhost -U watch1 $DB_NAME > $BACKUP_DIR/watch1_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/watch1_$DATE.sql

# Remove backups older than 30 days
find $BACKUP_DIR -name "watch1_*.sql.gz" -mtime +30 -delete

# Upload to S3 (optional)
aws s3 cp $BACKUP_DIR/watch1_$DATE.sql.gz s3://your-backup-bucket/
```

## Monitoring and Logging

### Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'watch1-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'watch1-postgres'
    static_configs:
      - targets: ['postgres:5432']

  - job_name: 'watch1-redis'
    static_configs:
      - targets: ['redis:6379']
```

### Grafana Dashboards

Create dashboards for:
- Application metrics
- Database performance
- System resources
- Media processing statistics
- User activity

### Log Aggregation

```yaml
# docker-compose.yml addition
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.5.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    ports:
      - "9200:9200"

  kibana:
    image: docker.elastic.co/kibana/kibana:8.5.0
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch

  logstash:
    image: docker.elastic.co/logstash/logstash:8.5.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    depends_on:
      - elasticsearch
```

## Performance Optimization

### Backend Optimization

```python
# backend/app/core/config.py
class Settings(BaseSettings):
    # Database connection pooling
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 30
    
    # Redis connection pooling
    REDIS_MAX_CONNECTIONS: int = 100
    
    # Media processing
    MAX_CONCURRENT_TRANSCODING: int = 4
    THUMBNAIL_BATCH_SIZE: int = 10
    
    # Caching
    CACHE_TTL: int = 3600
    ENABLE_QUERY_CACHE: bool = True
```

### Frontend Optimization

```typescript
// vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['vue', 'vue-router', 'pinia'],
          ui: ['@headlessui/vue', '@heroicons/vue']
        }
      }
    }
  }
})
```

### Nginx Optimization

```nginx
# nginx.conf
worker_processes auto;
worker_connections 1024;

http {
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    
    # Caching
    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=upload:10m rate=1r/s;
}
```

## Security Hardening

### Firewall Configuration

```bash
# UFW rules
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Docker Security

```yaml
# docker-compose.yml
services:
  backend:
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
    user: "1000:1000"
    cap_drop:
      - ALL
    cap_add:
      - CHOWN
      - SETGID
      - SETUID
```

### Application Security

```python
# backend/app/core/config.py
class Settings(BaseSettings):
    # Security headers
    SECURE_SSL_REDIRECT: bool = True
    SECURE_HSTS_SECONDS: int = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS: bool = True
    SECURE_HSTS_PRELOAD: bool = True
    
    # CORS
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOWED_ORIGINS: List[str] = ["https://yourdomain.com"]
    
    # Rate limiting
    RATELIMIT_STORAGE_URL: str = "redis://redis:6379"
    RATELIMIT_DEFAULT: str = "1000/hour"
```

## Backup and Recovery

### Automated Backups

```bash
#!/bin/bash
# backup_all.sh

# Database backup
./backup.sh

# Media files backup
rsync -av /app/media/ /backups/media/

# Configuration backup
tar -czf /backups/config_$(date +%Y%m%d).tar.gz \
    docker-compose.yml \
    nginx/ \
    .env.production

# Upload to cloud storage
aws s3 sync /backups/ s3://your-backup-bucket/
```

### Disaster Recovery

1. **Document recovery procedures**
2. **Test backup restoration**
3. **Maintain off-site backups**
4. **Implement monitoring alerts**
5. **Create runbooks for common issues**

## Scaling Considerations

### Horizontal Scaling

- Use load balancers for multiple backend instances
- Implement database read replicas
- Use Redis Cluster for caching
- Consider CDN for static assets

### Vertical Scaling

- Monitor resource usage
- Scale up based on metrics
- Optimize database queries
- Implement connection pooling

## Maintenance

### Regular Tasks

- **Daily**: Monitor logs and metrics
- **Weekly**: Review security updates
- **Monthly**: Test backup restoration
- **Quarterly**: Performance review and optimization

### Update Procedures

1. **Test updates in staging**
2. **Create database migrations**
3. **Backup before updates**
4. **Deploy during maintenance windows**
5. **Monitor after deployment**

## Troubleshooting

### Common Issues

**High memory usage**
- Check for memory leaks
- Optimize database queries
- Increase server resources

**Slow media processing**
- Check FFmpeg performance
- Optimize transcoding settings
- Use faster storage

**Database connection errors**
- Check connection limits
- Monitor database performance
- Optimize queries

### Health Checks

```bash
#!/bin/bash
# health_check.sh

# Check backend health
curl -f http://localhost:8000/health || exit 1

# Check database connectivity
pg_isready -h localhost -p 5432 || exit 1

# Check Redis connectivity
redis-cli ping || exit 1

echo "All services healthy"
```

This deployment guide provides comprehensive instructions for deploying Watch1 Media Server to production environments with proper security, monitoring, and scalability considerations.
