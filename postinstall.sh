# postinstall.sh  (make it executable:  chmod +x postinstall.sh)
#!/usr/bin/env bash
set -e
if command -v git-lfs >/dev/null 2>&1; then
  echo "Fetching Git-LFS assets…"
  git lfs install --local
  git lfs pull
fi