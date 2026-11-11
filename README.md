# DevOps Delivery Lab

Delivery and operations of a small API backed by PostgreSQL: reproducible infrastructure, Kubernetes deployments, observability and recovery.

**Status:** Stage 0 — repository setup. Next: a containerized service.

## Planned stack

| Area | Tools |
| --- | --- |
| Application | Python, FastAPI, PostgreSQL |
| Containers | Docker, Docker Compose |
| CI | GitHub Actions, GHCR, Trivy |
| Infrastructure | Terraform, Ansible, Linux |
| Delivery | Kubernetes, Helm, Argo CD |
| Observability | Prometheus, Grafana, Loki, Alertmanager |
| Operations | TLS, RBAC, backups, restore drills, load testing |

## Roadmap

- [ ] Containerized API, database and health checks
- [ ] CI checks, image builds and registry publishing
- [ ] Infrastructure provisioning and host configuration
- [ ] Kubernetes workloads, networking and persistent storage
- [ ] Helm packaging and GitOps delivery
- [ ] Metrics, dashboards, logs and actionable alerts
- [ ] Access controls, backup and verified recovery
- [ ] Load testing, failure drills and operational runbooks

Implementation tasks and acceptance criteria are tracked in [Issues](https://github.com/666Daredevil666/devops-delivery-lab/issues).
