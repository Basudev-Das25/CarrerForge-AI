# Installation Guide

## System Requirements

- **OS**: Windows 10 or later (64-bit)
- **RAM**: 4 GB minimum, 8 GB recommended
- **Disk**: 500 MB free space
- **Display**: 1280×720 minimum

## Option 1: Installer (Recommended)

1. Download `CareerForgeAI_Setup_v0.5.0-alpha.exe` from [Releases](https://github.com/Basudev-Das/CareerForge-AI/releases)
2. Run the installer
3. Follow the on-screen instructions
4. Launch CareerForge AI from Start Menu or Desktop shortcut

The installer:
- Installs to `C:\Program Files\CareerForge AI\`
- Creates Desktop and Start Menu shortcuts
- Sets up automatic updates
- Registers uninstall entry

## Option 2: Portable

1. Download `CareerForgeAI_Portable_v0.5.0-alpha.zip` from [Releases](https://github.com/Basudev-Das/CareerForge-AI/releases)
2. Extract to any folder (e.g., `C:\Apps\CareerForge AI\`)
3. Run `CareerForge AI.exe`

The portable version:
- Stores data in the extraction folder
- No installation required
- Can be moved between computers
- Does not register in Add/Remove Programs

## First Launch

1. The onboarding wizard guides you through initial setup
2. Choose an AI provider (OpenAI, Claude, Ollama, etc.)
3. Enter your API key (or use Ollama for local models)
4. Select a default resume template
5. Start building your profile

## Troubleshooting

### "Windows protected your PC"
- Click "More info" → "Run anyway"
- The app is not code-signed yet (alpha release)

### Application won't start
- Ensure Windows 10+ is installed
- Try running as Administrator
- Check Windows Defender exclusions

### AI features not working
- Ensure you have a valid API key configured
- Check your internet connection
- For Ollama: ensure Ollama is running (`ollama serve`)

### PDF generation fails
- Install Typst: `winget install typst.typst`
- Or use text/Markdown export as alternative

## Data Storage

All data is stored locally:
- **Windows**: `%USERPROFILE%\.careerforge\`
- **Database**: `.careerforge\careerforge.db`
- **Settings**: `.careerforge\settings.json`
- **Backups**: `.careerforge\backups\`
- **Logs**: `.careerforge\logs\`
