#!/bin/bash
# Script: package_zelos.sh
# Purpose: Collect zelos + dependencies into a tarball for transfer (e.g., Termux)

set -e

# Output tar file
OUTPUT_TAR="zelos-packages.tar.gz"

# Temporary directory to gather everything
TMPDIR=$(mktemp -d)
echo "[*] Using temporary directory: $TMPDIR"

# Detect Python user site-packages
SITE_PACKAGES=$(python3 -m site --user-site)
echo "[*] User site-packages: $SITE_PACKAGES"

# Copy zelos installed packages
echo "[*] Copying installed Python packages..."
cp -r "$SITE_PACKAGES" "$TMPDIR/"

# Copy console scripts from bin directory
BIN_DIR=$(python3 -m site --user-base)/bin
echo "[*] Copying console scripts from $BIN_DIR..."
mkdir -p "$TMPDIR/bin"
cp -r "$BIN_DIR/zelos"* "$TMPDIR/bin/" 2>/dev/null || true

# Optional: Copy any additional config files if needed
# cp path/to/config "$TMPDIR/config/"

# Create tar.gz archive
echo "[*] Creating tar archive $OUTPUT_TAR..."
tar -czf "$OUTPUT_TAR" -C "$TMPDIR" .

# Clean up
rm -rf "$TMPDIR"

echo "[✓] Done! Tar file created: $OUTPUT_TAR"
echo "You can now transfer it to Termux or another environment."