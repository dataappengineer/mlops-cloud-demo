# Issue: Refactor Repository Structure for Production-Grade Organization

## 🎯 Context
After 4 months of working on client projects, I'm resuming development of this MLOps portfolio project. Before continuing with new features, I need to address technical debt: the repository structure has grown organically and lacks the organization needed for a production-grade system.

## 🐛 Current Problems

### Structural Issues:
1. **Airflow infrastructure scattered in root** (`Dockerfile.airflow`, `docker-compose.airflow.yaml`)
2. **Unclear dependency ownership** (`requirements.txt` in root - which component?)
3. **Security concerns** (`.env` exposed at root level)
4. **IaC files mixed with application code** (`main.tf` in root)
5. **Inconsistent component organization** (model-api is well-structured, data-pipeline is not)

### Impact:
- ❌ Difficult for collaborators/clients to navigate
- ❌ Unclear separation of concerns
- ❌ Harder to deploy individual components
- ❌ Not following industry monorepo standards
- ❌ Credentials management unclear

## ✅ Proposed Solution

Restructure following **industry monorepo best practices** (similar to Google, Uber, Netflix):

```
mlops-cloud-demo/
├── README.md
├── .gitignore
├── docs/                        # All documentation
│   ├── aws-setup/
│   ├── data-pipeline/
│   └── model-api/
├── infrastructure/              # IaC isolated
│   ├── terraform/
│   │   ├── main.tf
│   │   └── .env
│   └── README.md
├── data-pipeline/              # Self-contained Airflow component
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── requirements.txt
│   ├── .env.example
│   ├── dags/
│   ├── data/
│   └── README.md
└── model-api/                  # Already well-structured ✅
    ├── Dockerfile
    ├── docker-compose.yml
    └── app/
```

## 🎓 Learning Objectives

This refactoring addresses:
1. **Monorepo patterns** - How large companies organize multi-component systems
2. **Component isolation** - Each service can be developed/deployed independently
3. **Security best practices** - Credentials properly scoped and documented
4. **Developer experience** - Clear navigation, consistent structure

## 📚 Research & References

- **Google's Monorepo Strategy**: Component isolation with clear boundaries
- **Netflix Tech Blog**: Microservices structure and IaC separation
- **12-Factor App**: Config management and environment variables
- **Docker Compose Best Practices**: Multi-service organization

## 🔨 Implementation Steps

- [ ] Create `infrastructure/terraform/` directory
- [ ] Move `main.tf` and related files
- [ ] Create `infrastructure/.env.example` template
- [ ] Move Airflow files into `data-pipeline/`
- [ ] Create component-specific `requirements.txt`
- [ ] Create `.env.example` for each component
- [ ] Update all relative paths in configs
- [ ] Update documentation with new structure
- [ ] Test all components still work post-migration
- [ ] Update README with architecture diagram

## 📊 Success Criteria

- ✅ Each component is self-contained and independently runnable
- ✅ No files in root except README, .gitignore
- ✅ Clear separation: docs/, infrastructure/, data-pipeline/, model-api/
- ✅ All services start successfully with docker-compose
- ✅ Documentation updated to reflect new structure

## 💡 Portfolio Value

**This demonstrates:**
- Ability to recognize and address technical debt
- Knowledge of production-grade repository patterns
- Prioritizing maintainability over "just making it work"
- Understanding of multi-component system architecture
- Professional software engineering discipline

---

**Related Issues:** #3 (Data Pipeline), #5 (Model API)
**Status:** Todo → In Progress
**Priority:** High (blocking clean development of new features)
**Estimated Time:** 2-3 hours
