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

- [ ] Move deprecated folders to preserve them for comparison:
  - Move `builder/` folder to `outdated/builder/`
  - Move `src/` folder to `outdated/src/`
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
- [ ] Move old `worker-config.json` to `outdated/worker-config.json` (replaced by `hub.json`)

### Preservation & Compatibility

- [ ] Compare current `worker-sglang` files with `sglang/.runpod` equivalents
- [ ] Compare `outdated/src/` files with new root-level files to identify missing features
- [ ] Compare `outdated/builder/` setup with new structure requirements
- [ ] Compare `outdated/worker-config.json` with new `hub.json` for missing configurations
- [ ] Preserve any valuable additions or configurations from outdated structure
- [ ] Ensure environment variable compatibility is maintained
- [ ] Update any worker-specific customizations if needed

### Validation

- [ ] Verify Docker build succeeds with new structure
- [ ] Confirm RunPod Hub compatibility with new `hub.json`
- [ ] Test that all original functionality is preserved
- [ ] Validate that no critical features from `outdated/` folders are missing

### Cleanup (Final Step)

- [ ] Only after confirming no missing features: Remove `outdated/` folder and its contents

## Files to Review for Differences

- Compare `outdated/src/handler.py` vs `sglang/.runpod/handler.py` vs new `handler.py`
- Compare `outdated/src/engine.py` vs `sglang/.runpod/engine.py` vs new `engine.py`
- Compare `outdated/builder/` setup vs `sglang/.runpod/` structure requirements
- Compare `worker-sglang/Dockerfile` vs `sglang/.runpod/Dockerfile`
- Review `outdated/worker-config.json` vs `sglang/.runpod/hub.json` for missing configurations

## Success Metrics

- Worker builds successfully with new structure
- All original environment variables and configurations work
- RunPod Hub compatibility maintained
- Code is cleaner and follows modern structure
