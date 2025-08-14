# User Story: Add HuggingFace Token Support for Gated/Private Models

## Overview

Add HuggingFace token support to the SGLang worker to enable access to gated and private models from the HuggingFace Hub. This includes adding a secure password input field in the RunPod Hub configuration and ensuring the token is properly passed to the SGLang engine.

## Current State

- **hub.json**: Contains comprehensive model configuration options but lacks HuggingFace token support
- **engine.py**: SGLang engine initialization without HF_TOKEN environment variable
- **Dockerfile**: Container setup without HuggingFace token environment variable handling

## Goal

Enable the SGLang worker to access gated and private models from HuggingFace Hub by implementing secure token handling throughout the worker infrastructure.

## Acceptance Criteria

### RunPod Hub Configuration

- [ ] Add `HF_TOKEN` environment variable configuration to `hub.json`:
  - Use `password` type for secure input handling
  - Set as non-required (optional) field
  - Include descriptive text about gated/private model access
  - Position prominently alongside MODEL_PATH (not in advanced section)

### Environment Variable Integration

- [ ] Ensure `HF_TOKEN` environment variable is properly exported in Docker container
- [ ] Verify SGLang engine can access `HF_TOKEN` from environment
- [ ] Confirm token is passed to HuggingFace transformers library for model downloads

### Security & Best Practices

- [ ] Use `password` input type to mask token in RunPod Hub UI
- [ ] Ensure token is not logged or exposed in error messages
- [ ] Follow HuggingFace token security best practices
- [ ] Maintain compatibility with existing non-gated model workflows

### Validation

- [ ] Test worker with gated model (e.g., Llama models requiring approval)
- [ ] Test worker with private model (requires HF token)
- [ ] Verify worker continues to work with public models (without token)
- [ ] Confirm token is properly masked in RunPod Hub interface
- [ ] Validate Docker build succeeds with new configuration

### Documentation

- [ ] Update any relevant documentation about using gated/private models
- [ ] Ensure token field has clear description for users

## Implementation Details

### hub.json Changes

Add new environment variable configuration:

```json
{
  "key": "HF_TOKEN",
  "input": {
    "name": "HuggingFace Token",
    "type": "password",
    "description": "HuggingFace access token for gated and private models",
    "default": "",
    "required": false
  }
}
```

### Engine Integration

- Verify `HF_TOKEN` environment variable is available to SGLang engine
- Ensure HuggingFace transformers library automatically uses the token when set
- No explicit token passing required if environment variable is properly set

### Docker Environment

- Confirm Docker container inherits `HF_TOKEN` environment variable from RunPod
- Test that SGLang can access HuggingFace Hub with the provided token

## Files to Modify

- `.runpod/hub.json` - Add HF_TOKEN configuration
- Test with `engine.py` - Verify token usage (may not require code changes)
- Validate `Dockerfile` - Ensure environment variable handling (may not require changes)

## Success Metrics

- User can input HuggingFace token through RunPod Hub interface
- Token input is masked (password type) for security
- Worker successfully downloads and runs gated models when token is provided
- Worker continues to work with public models when no token is provided
- No token information is exposed in logs or error messages

## Testing Scenarios

1. **Public Model**: Test without HF_TOKEN (existing functionality)
2. **Gated Model**: Test with valid HF_TOKEN for gated model
3. **Private Model**: Test with valid HF_TOKEN for private model
4. **Invalid Token**: Test with invalid HF_TOKEN (should fail gracefully)
5. **UI Security**: Verify token is masked in RunPod Hub interface
