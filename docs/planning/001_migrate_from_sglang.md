# User Story: Migrate Worker-SGLang to Updated Structure

## Overview

Migrate the unmaintained `worker-sglang` to use the updated and maintained structure from `sglang/.runpod`, ensuring compatibility with RunPod Hub while preserving any valuable additions.

## Current State

- **worker-sglang**: Outdated structure with `builder/` and `src/` folders, unmaintained
- **sglang/.runpod**: Updated, maintained structure with modern RunPod Hub compatibility

## Goal

Update `worker-sglang` to match the modern structure while preserving functionality and ensuring RunPod Hub compatibility.

## Acceptance Criteria

### Structure Migration

- [ ] Remove deprecated `builder/` folder and its contents
- [ ] Remove deprecated `src/` folder and its contents
- [ ] Move core files from `sglang/.runpod/` to `worker-sglang/` root:
  - `handler.py`
  - `engine.py`
  - `utils.py`
  - `download_model.py`
  - `Dockerfile`
  - `docker-compose.yml`
  - `requirements.txt`
  - `test_input.json`
  - `public/` directory

### RunPod Hub Integration

- [ ] Create `worker-sglang/.runpod/` folder containing only:
  - `hub.json` (RunPod Hub configuration)
  - `tests.json` (Hub testing configuration)
- [ ] Remove old `worker-config.json` (replaced by `hub.json`)

### Preservation & Compatibility

- [ ] Compare current `worker-sglang` files with `sglang/.runpod` equivalents
- [ ] Preserve any valuable additions or configurations from current `worker-sglang`
- [ ] Ensure environment variable compatibility is maintained
- [ ] Update any worker-specific customizations if needed

### Validation

- [ ] Verify Docker build succeeds with new structure
- [ ] Confirm RunPod Hub compatibility with new `hub.json`
- [ ] Test that all original functionality is preserved

## Files to Review for Differences

- Compare `worker-sglang/src/handler.py` vs `sglang/.runpod/handler.py`
- Compare `worker-sglang/src/engine.py` vs `sglang/.runpod/engine.py`
- Compare `worker-sglang/Dockerfile` vs `sglang/.runpod/Dockerfile`
- Review `worker-sglang/worker-config.json` vs `sglang/.runpod/hub.json` for missing configurations

## Success Metrics

- Worker builds successfully with new structure
- All original environment variables and configurations work
- RunPod Hub compatibility maintained
- Code is cleaner and follows modern structure
