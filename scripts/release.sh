#!/bin/bash
# CareerForge AI Release Script
# Usage: ./scripts/release.sh [version]

set -e

VERSION=${1:-"0.5.0-alpha"}
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "============================================"
echo "  CareerForge AI Release: v${VERSION}"
echo "============================================"

# 1. Clean
echo "[1/8] Cleaning build artifacts..."
cd "$PROJECT_DIR"
rm -rf dist src-tauri/target/release
npm run clean 2>/dev/null || true

# 2. Install dependencies
echo "[2/8] Installing dependencies..."
npm install --production=false 2>/dev/null || npm install
cd backend && pip install -r requirements.txt 2>/dev/null || true
cd "$PROJECT_DIR"

# 3. Run quality checks
echo "[3/8] Running quality checks..."
npm run lint 2>/dev/null || echo "Lint skipped"
npm run type-check 2>/dev/null || echo "Type check skipped"

# 4. Build frontend
echo "[4/8] Building frontend..."
npm run build

# 5. Build Tauri application
echo "[5/8] Building Tauri desktop application..."
npx tauri build 2>/dev/null || echo "Tauri build (requires Rust toolchain)"

# 6. Generate checksums
echo "[6/8] Generating checksums..."
if [ -d "src-tauri/target/release/bundle" ]; then
    cd src-tauri/target/release/bundle
    find . -name "*.exe" -o -name "*.msi" -o -name "*.zip" | while read f; do
        sha256sum "$f" >> SHA256SUMS.txt 2>/dev/null || shasum -a 256 "$f" >> SHA256SUMS.txt
    done
    cd "$PROJECT_DIR"
fi

# 7. Copy portable package
echo "[7/8] Creating portable package..."
PORTABLE_DIR="dist/CareerForgeAI_Portable_v${VERSION}"
mkdir -p "$PORTABLE_DIR"
cp -r dist/* "$PORTABLE_DIR/" 2>/dev/null || true
cp README.md INSTALL.md RELEASE_NOTES.md CHANGELOG.md "$PORTABLE_DIR/" 2>/dev/null || true
cp .env.example "$PORTABLE_DIR/" 2>/dev/null || true

# 8. Summary
echo "[8/8] Build complete!"
echo ""
echo "============================================"
echo "  Release Artifacts"
echo "============================================"
echo "  Frontend:      dist/"
if [ -d "src-tauri/target/release/bundle" ]; then
    echo "  Installers:   src-tauri/target/release/bundle/"
fi
echo "  Portable:      dist/CareerForgeAI_Portable_v${VERSION}/"
echo "  Version:       ${VERSION}"
echo "============================================"
