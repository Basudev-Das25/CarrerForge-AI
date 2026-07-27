# Known Issues — v0.5.0-alpha

## Critical

None reported.

## High

### PDF Rendering Requires Typst
- **Description**: Typst must be installed to compile resume PDFs
- **Impact**: Portable users need to install Typst separately
- **Workaround**: Export as text or Markdown
- **Fix planned**: Bundle Typst binary in release

## Medium

### Document Vault Placeholder
- **Description**: The Document Vault page shows "coming soon"
- **Impact**: Cannot upload or manage documents
- **Workaround**: Use profile sections to manage data
- **Fix planned**: Phase 2 implementation

### Settings Placeholder
- **Description**: The Settings page shows "coming soon"
- **Impact**: Cannot access settings from the menu
- **Workaround**: Update settings are accessible via Updates page
- **Fix planned**: Full settings panel in next release

### Help Center Placeholder
- **Description**: The Help page shows "coming soon"
- **Impact**: No in-app help available
- **Workaround**: Refer to docs/ directory
- **Fix planned**: Full help center in next release

## Low

### Template Preview Thumbnails
- **Description**: Template previews show a file icon instead of actual preview
- **Impact**: Cannot see template appearance before selecting
- **Workaround**: Select and preview in the generator
- **Fix planned**: Generate preview images for each template

### Ollama Model Management
- **Description**: Cannot download or switch Ollama models from within the app
- **Impact**: Users must manage models via Ollama CLI
- **Workaround**: Use `ollama pull <model>` command
- **Fix planned**: Model management UI in settings

### Multi-Page Resume Typst Compilation
- **Description**: Very long resumes may cause Typst compilation to produce warnings
- **Impact**: PDF may have minor formatting issues on 3+ page resumes
- **Workaround**: Keep resume concise (1-2 pages)
- **Fix planned**: Improve template overflow handling

## Platform

### Windows Only
- **Description**: v0.5.0-alpha is Windows-only
- **Impact**: macOS and Linux users cannot run the application
- **Fix planned**: Cross-platform builds in future releases
