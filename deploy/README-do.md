# DigitalOcean Deployment Notes

Preferred: App Platform using container registry.

Steps:

1. Build and tag image:

```bash
docker build -t registry.digitalocean.com/<registry>/usage-service:latest .
```

2. Push to DO registry (login via doctl):

```bash
doctl registry login
docker push registry.digitalocean.com/<registry>/usage-service:latest
```

3. Create app from `app.yaml`:

```bash
doctl apps create --spec app.yaml
```

If DO access is not available, push to Docker Hub and use the same `app.yaml` with the image path replaced.
