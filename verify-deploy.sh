#!/bin/bash
# Terry Game Lab - Full Verification After Deployment
# Compares local file hash with remote file hash, ensures 100% consistency

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🔍 Starting full deployment verification..."
echo "=================================================="

# Wait for GitHub to update
echo "⏳ Waiting 10 seconds for GitHub to update..."
sleep 10

# Download each HTML file from GitHub raw and compare hash
FAILED=0

for file in index.html methodology.html methodology-full.html test-crt.html; do
    echo ""
    echo "📄 Verifying $file..."
    
    # Local file check
    if [ ! -f "$file" ]; then
        echo -e "${RED}❌ ERROR: Local file $file not found${NC}"
        FAILED=1
        continue
    fi
    
    LOCAL_SIZE=$(wc -c < "$file")
    LOCAL_HASH=$(sha256sum "$file" | awk '{print $1}')
    echo "   Local:  $LOCAL_HASH ($LOCAL_SIZE bytes)"
    
    # Download from GitHub
    REMOTE_URL="https://raw.githubusercontent.com/ypingzhao/terry-game-lab/main/$file"
    TMP_FILE="/tmp/verify-$file"
    
    echo "   Downloading from GitHub..."
    if ! wget -q -O "$TMP_FILE" "$REMOTE_URL" --timeout=10; then
        echo -e "${RED}❌ ERROR: Failed to download $file from GitHub${NC}"
        FAILED=1
        rm -f "$TMP_FILE"
        continue
    fi
    
    REMOTE_SIZE=$(wc -c < "$TMP_FILE")
    REMOTE_HASH=$(sha256sum "$TMP_FILE" | awk '{print $1}')
    echo "   Remote: $REMOTE_HASH ($REMOTE_SIZE bytes)"
    
    if [ "$LOCAL_HASH" = "$REMOTE_HASH" ] && [ "$LOCAL_SIZE" = "$REMOTE_SIZE" ]; then
        echo -e "${GREEN}✅ PASS: Hash matches 100%${NC}"
    else
        echo -e "${RED}❌ FAIL: Hash mismatch!${NC}"
        echo -e "${RED}   Local:  $LOCAL_HASH ($LOCAL_SIZE bytes)${NC}"
        echo -e "${RED}   Remote: $REMOTE_HASH ($REMOTE_SIZE bytes)${NC}"
        FAILED=1
    fi
    
    rm -f "$TMP_FILE"
done

echo ""
echo "=================================================="

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ ALL FILES VERIFIED: 100% consistent between local and GitHub${NC}"
    echo -e "${GREEN}✅ GitHub Pages will show the correct content after cache refresh${NC}"
    echo ""
    echo "🌐 Visit your site:"
    echo "   https://ypingzhao.github.io/terry-game-lab/"
    echo "   https://ypingzhao.github.io/terry-game-lab/methodology-full.html"
    echo ""
    echo "💡 To bypass browser cache: Press Ctrl+F5 (Windows/Linux) or Cmd+Shift+R (Mac)"
    exit 0
else
    echo -e "${RED}❌ Some files failed verification! Check errors above.${NC}"
    echo -e "${YELLOW}💡 Recommendation: Re-run ./deploy.sh then ./verify-deploy.sh${NC}"
    exit 1
fi
