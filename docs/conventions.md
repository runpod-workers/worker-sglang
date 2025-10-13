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
refactor(engine): migrate from MODEL_PATH to MODEL_NAME
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
