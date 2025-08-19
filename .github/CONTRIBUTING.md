# Contributing to SGLang Worker

Welcome! This guide explains how to develop and deploy the SGLang Worker for RunPod.

## 📋 Prerequisites

- Docker with linux/amd64 support
- Git
- Access to RunPod Hub (for testing)

## 🛠️ Development Workflow

### 1. Follow Conventions Strictly

**⚠️ IMPORTANT**: Read and follow [`docs/conventions.md`](../docs/conventions.md) strictly.

**Key Rules:**

- Use Angular conventional commit messages
- Never commit without explicit permission
- Follow code quality guidelines

### 2. Development Setup

```bash
# Clone the repository
git clone <repo-url>
cd worker-sglang

# Create .env file for Hugging Face token (required for gated models)
echo "HF_TOKEN=your_huggingface_token_here" > .env

# Build locally for testing (optional - will be built in CI)
docker build --platform linux/amd64 -t worker-sglang-local .

# Test with docker-compose (will automatically use .env file)
docker-compose up
```

### 3. Environment Configuration

The project uses a `.env` file for local development. Docker Compose automatically reads this file.

**Required for local testing:**

```bash
# .env file (create in project root)
HF_TOKEN=your_huggingface_token_here
```

**Getting your HF_TOKEN:**

1. Go to [Hugging Face Settings](https://huggingface.co/settings/tokens)
2. Create a new token with "Read" permissions
3. Copy the token to your `.env` file

**⚠️ Security Note:**

- Never commit the `.env` file to git
- The `.env` file is already in `.gitignore`
- Use environment variables in production/CI

### 4. Making Changes

1. **Create feature branch:**

   ```bash
   git checkout -b feat/your-feature-name
   ```

2. **Make your changes** to:

   - Core files in project root
   - Configuration files
   - Documentation

3. **Test your changes:**

   ```bash
   # Test Docker build
   docker build --platform linux/amd64 -t test-build .

   # Test with sample input (ensure .env file exists first)
   docker run --rm test-build python3 -c "import handler; print('Import successful')"

   # Test with docker-compose (uses .env automatically)
   docker-compose up
   ```

4. **Commit following conventions:**
   ```bash
   # Examples:
   git commit -m "feat(handler): add new openai compatibility feature"
   git commit -m "fix(engine): resolve model loading issue"
   git commit -m "docs(readme): update deployment instructions"
   ```

## 🚀 Deployment

### Development Deployment

**Trigger:** Push to **any** branch

```bash
# Push feature branch for testing
git push origin feat/your-feature-name

# Or push to main
git checkout main
git merge feat/your-feature-name
git push origin main
```

**Result:**

- ✅ Triggers `.github/workflows/dev.yml`
- ✅ Builds image: `runpod/worker-sglang:<branch-name>`
- ✅ Available for testing on RunPod

**Use for:** Testing any branch, development, staging environments

### Production Release

**Trigger:** Create and push git tag

```bash
# Create release tag (use semantic versioning)
git tag v1.2.3
git push origin v1.2.3
```

**Result:**

- ✅ Triggers `.github/workflows/release.yml`
- ✅ Builds image: `runpod/worker-sglang:v1.2.3`
- ✅ Production-ready release

**Use for:** Production deployments, stable releases

## 📦 Docker Images

| **Image**                            | **Trigger**        | **Purpose**         |
| ------------------------------------ | ------------------ | ------------------- |
| `runpod/worker-sglang:<branch-name>` | Push to any branch | Development/testing |
| `runpod/worker-sglang:v1.2.3`        | Git tag `v1.2.3`   | Production release  |

## 🏗️ Build Configuration

### Docker Bake

The project uses `docker-bake.hcl` for build configuration:

```bash
# Build locally using bake
docker buildx bake

# Build with custom variables
RELEASE_VERSION=test docker buildx bake
```

### Environment Variables

Configure via GitHub repository settings:

| **Variable**     | **Default**     | **Description**       |
| ---------------- | --------------- | --------------------- |
| `DOCKERHUB_REPO` | `runpod`        | Docker Hub repository |
| `DOCKERHUB_IMG`  | `worker-sglang` | Image name            |

### Secrets Required

| **Secret**                 | **Required** | **Description**          |
| -------------------------- | ------------ | ------------------------ |
| `DOCKERHUB_USERNAME`       | ✅           | Docker Hub username      |
| `DOCKERHUB_TOKEN`          | ✅           | Docker Hub access token  |
| `HUGGINGFACE_ACCESS_TOKEN` | ❌           | For private model access |

## 🧪 Testing

### Local Testing

```bash
# Build and test locally
docker build --platform linux/amd64 -t worker-sglang-test .

# Run basic functionality test
docker run --rm worker-sglang-test python3 -c "
import handler
import engine
print('Core modules imported successfully')
"
```

### RunPod Testing

1. **Development builds** (`:<branch-name>`):

   - Deploy on RunPod using `runpod/worker-sglang:<branch-name>`
   - Test with real workloads from any branch

2. **Release builds** (`:v1.2.3`):
   - Deploy on RunPod using `runpod/worker-sglang:v1.2.3`
   - Validate in production environment

## 📁 Project Structure

```
worker-sglang/
├── .runpod/                  # Main worker files
│   ├── handler.py           # Request handler
│   ├── engine.py            # SGLang engine
│   ├── utils.py             # Utilities
│   ├── hub.json             # RunPod Hub config
│   └── requirements.txt     # Python dependencies
├── .github/
│   ├── workflows/
│   │   ├── dev.yml          # Development builds
│   │   └── release.yml      # Release builds
│   └── CONTRIBUTING.md      # This file
├── docs/
│   └── conventions.md       # Development conventions
├── outdated/                # Legacy code (for reference)
├── Dockerfile               # Container definition
├── docker-bake.hcl         # Build configuration
└── docker-compose.yml      # Local development
```

## 🤝 Contributing Guidelines

1. **Read conventions:** Always follow [`docs/conventions.md`](../docs/conventions.md)
2. **Test thoroughly:** Ensure your changes work locally and on RunPod
3. **Document changes:** Update documentation for significant changes
4. **Use proper commits:** Follow Angular conventional commit format
5. **Ask questions:** Don't hesitate to ask for help or clarification

## 🐛 Troubleshooting

### Build Issues

```bash
# Check build context
docker buildx bake --print

# Build with verbose output
docker build --platform linux/amd64 --progress=plain -t debug-build .
```

### Deployment Issues

1. **Check GitHub Actions logs** in the Actions tab
2. **Verify secrets** are configured correctly
3. **Test locally first** before pushing

## 📝 Release Process

1. **Develop** on feature branch
2. **Test** branch build (triggers `:<branch-name>` image)
3. **Merge** to main when ready
4. **Test** the `:main` image on RunPod
5. **Tag** for release when ready (from main)
6. **Deploy** the `:v1.2.3` image to production

Happy contributing! 🚀
