# Development Conventions

## Git Commit Rules

### When AI Assistant CAN Commit

- ❌ **NEVER** commit automatically
- ✅ **ONLY** when explicitly asked: "commit this" / "please commit" / "make a commit"
- ✅ **MUST** receive explicit permission for EVERY commit

### When AI Assistant CANNOT Commit

- ❌ After completing tasks/migrations
- ❌ When "finishing up" work
- ❌ At the end of conversations
- ❌ Without explicit user instruction

## Commit Message Format

**MUST** use Angular Conventional Commits style:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Types

- `feat`: new feature
- `fix`: bug fix
- `docs`: documentation only changes
- `style`: formatting, missing semi colons, etc
- `refactor`: code change that neither fixes a bug nor adds a feature
- `perf`: performance improvements
- `test`: adding missing tests
- `chore`: changes to build process or auxiliary tools
- `ci`: changes to CI configuration files and scripts

### Examples

```bash
feat(docker): add github workflow for automated builds
fix(handler): resolve openai compatibility issue
docs(readme): update installation instructions
refactor(engine): migrate from MODEL_NAME to MODEL_PATH
chore(deps): update requirements.txt
```

### Scope Guidelines

- Use component names: `docker`, `handler`, `engine`, `workflow`, `deps`
- Keep scopes short and descriptive
- Optional but recommended

## Code Quality

- Follow existing code style
- Test changes before committing
- Write descriptive commit messages
- Keep commits focused and atomic

## Configuration Conventions

- Single source of truth: use `.runpod/hub.json` for endpoint configuration.

  - Define environment variables, UI options, and allowed CUDA versions here.
  - Do not add or rely on `worker-config.json` (removed).

- CUDA policy:

  - Minimum supported CUDA is 12.6.
  - Base images must match this (e.g., `lmsysorg/sglang:vX.Y.Z-cu126`).
  - Keep `allowedCudaVersions` in `hub.json` at 12.6 or higher.

- Tool/function calling and reasoning:
  - `TOOL_CALL_PARSER`: required to enable tool/function calling; no runtime default is applied. If unset, `--tool-call-parser` is not passed to SGLang.
  - `REASONING_PARSER`: required to enable reasoning trace parsing; no runtime default is applied. If unset, `--reasoning-parser` is not passed to SGLang.
  - Choose a parser matching the model family (e.g., `llama3`, `llama4`, `mistral`, `qwen25`, `deepseekv3`).
