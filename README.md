# HelpDesk — Support Ticket Management

HelpDesk is a support-ticket tracker: staff log customer issues, assign them, set a priority and move them through
`open → in_progress → resolved → closed`. A dashboard shows live KPI counts and a filterable ticket table.
The project also demonstrates a complete DevOps path: tests → Docker → CI/CD → security scan → Terraform (AWS EKS) → Helm → monitoring.

```
Developer → GitHub → GitHub Actions (pytest, frontend build, Docker build, Trivy, push to GHCR)
                                      │
                    Terraform → AWS VPC + EKS → Helm → frontend (React/Nginx) + backend (FastAPI) + PostgreSQL
                                                              │
                                                    Prometheus → Grafana
```

## Demo

Recorded walkthrough (commit → pipeline → GHCR image → `helm upgrade` on EKS → updated app):
[Watch the demo](https://drive.google.com/file/d/1akWYIZ53DCBeI_8r9EHGJC3Ik-XkhUro/view?usp=sharing)

Evidence screenshots for every module are in [`docs/screenshots/`](docs/screenshots/).

## Stack

| Layer | Tech |
|-------|------|
| Frontend | React 18 + Vite, responsive CSS, served by unprivileged Nginx |
| Backend | FastAPI, SQLAlchemy 2, Alembic, `prometheus-fastapi-instrumentator` |
| Database | PostgreSQL 16 |
| Tests | pytest (in-memory SQLite, never the real DB) |
| CI/CD | GitHub Actions, Trivy, GHCR (images tagged with the commit SHA) |
| IaC | Terraform: VPC (2 public + 2 private subnets) + EKS managed node group |
| Deploy | Kubernetes + Helm (2 replicas each, ClusterIP services, Ingress, HPA) |
| Observability | kube-prometheus-stack (Prometheus + Grafana), ServiceMonitor |

## REST API

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/tickets?status=&priority=` | list / filter tickets |
| GET | `/api/tickets/{id}` | get one |
| POST | `/api/tickets` | create |
| PUT | `/api/tickets/{id}` | update (partial) |
| DELETE | `/api/tickets/{id}` | delete |
| GET | `/api/tickets/stats` | counts for the dashboard |
| GET | `/health`, `/ready`, `/metrics` | liveness, readiness (checks DB), Prometheus metrics |

Swagger UI: `http://localhost:8000/docs`

## Run locally (Docker Compose)

```bash
docker compose up --build
```
App: <http://localhost:3000> · API docs: <http://localhost:8000/docs> · Metrics: <http://localhost:8000/metrics>
Stop with `docker compose down` (add `-v` to wipe the database volume). Copy `.env.example` to `.env` to change DB credentials.

## Run tests

```bash
cd backend
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -v
```

## CI/CD (`.github/workflows/ci.yml`)

On every push to `main`:
1. **test** — `pytest` (the build fails if any test fails) and `npm run build` for the frontend.
2. **build-scan-push** (matrix: backend, frontend) — build image → **Trivy scan (fails on HIGH/CRITICAL)** → push to
   `ghcr.io/<owner>/<repo>-{backend,frontend}:<git-sha>`. Images are never tagged `latest`.
3. **deploy** (optional) — `helm upgrade --install` against a cluster; enabled by setting the repo variable
   `DEPLOY_ENABLED=true` and the secret `KUBECONFIG_B64`.

### Security scan explanation
Trivy scans each built image's OS packages (Debian for the backend, Alpine for the frontend) and Python packages for known CVEs.
On the first run it reported HIGH findings — e.g. **CVE-2026-48818 in starlette 0.41.3** (SSRF via UNC paths in `StaticFiles`) and
OpenSSL/libexpat issues in the old Alpine base. I fixed them by upgrading FastAPI/Starlette, moving to the current
`nginx-unprivileged` base with `apk upgrade`, and removing pip/setuptools from the runtime image. The scan is now clean and the pipeline gates on it.

## Infrastructure (Terraform)

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars   # no credentials in this file
terraform init && terraform plan && terraform apply
$(terraform output -raw configure_kubectl)
terraform destroy                              # always destroy afterwards to avoid AWS charges
```

## Deploy to Kubernetes (Helm)

```bash
# 1. Monitoring first (installs the ServiceMonitor CRD)
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace -f monitoring/prometheus-values.yaml
kubectl apply -f monitoring/dashboard-configmap.yaml

# 2. Ingress controller (e.g. ingress-nginx)
helm upgrade --install ingress-nginx ingress-nginx --repo https://kubernetes.github.io/ingress-nginx \
  -n ingress-nginx --create-namespace

# 3. The app
kubectl apply -f k8s/namespace.yaml
helm upgrade --install helpdesk ./helm/helpdesk -n helpdesk \
  -f helm/helpdesk/values-dev.yaml \
  --set backend.image.repository=ghcr.io/<owner>/<repo>-backend \
  --set frontend.image.repository=ghcr.io/<owner>/<repo>-frontend \
  --set backend.image.tag=<git-sha> --set frontend.image.tag=<git-sha> \
  --set postgres.password=<strong-password>

kubectl get pods -n helpdesk && kubectl get svc -n helpdesk && helm list -n helpdesk
```
Make the GHCR packages public (or add `imagePullSecrets`) so the cluster can pull them.
Open the app at the ingress load-balancer address with `Host: helpdesk.local` (add an `/etc/hosts` entry).

## Monitoring

```bash
kubectl port-forward -n monitoring svc/kube-prometheus-stack-prometheus 9090   # Status → Targets
kubectl port-forward -n monitoring svc/kube-prometheus-stack-grafana 3001:80   # dashboard "HelpDesk API"
scripts/load-test.sh http://localhost:8000 60                                  # generate traffic
```

## Repository layout

```
backend/      FastAPI app, Alembic migrations, tests, Dockerfile
frontend/     React app, Nginx config, Dockerfile
terraform/    AWS VPC + EKS
helm/helpdesk Helm chart        k8s/  namespace manifest
monitoring/   Prometheus/Grafana values + dashboard     scripts/  load generator
.github/workflows/ci.yml        docker-compose.yml
```
