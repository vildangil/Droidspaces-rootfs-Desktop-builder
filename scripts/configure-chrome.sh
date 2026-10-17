#!/usr/bin/env bash
# Compatibility alias for old local build scripts; new images install Firefox.
# Google Chrome is no longer downloaded or installed by DroidSpaces.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$here/configure-firefox.sh" "$@"
