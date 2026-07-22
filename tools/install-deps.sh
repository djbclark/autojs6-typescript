#!/usr/bin/env bash
# Install this toolkit's dependencies on macOS, the major Linux distros, and
# Termux (Android). This is the ONE shell script in the project — detecting
# "which package manager am I on" is inherently a shell/OS-probing task; the
# actual tools (tsc, rhino_check.py, etc.) are just/python as usual. Run
# directly (`bash tools/install-deps.sh`) or via `just install-deps`.
#
# Installs:
#   node   — compiles TypeScript (tsc)
#   python3 — tools/*.py (find_rhino_jar, rhino_check, print_rhino_version,
#             check_require_bindings)
#   java   — only needed for the real-Rhino checks (check-clean/find-errors);
#             everything else works without it
#   just   — task runner this whole toolkit is driven through
set -eu

log() { printf '%s\n' "$*" >&2; }

install_macos() {
  if ! command -v brew >/dev/null 2>&1; then
    log "error: Homebrew not found. Install it first: https://brew.sh"
    exit 1
  fi
  brew install node python just openjdk
  # openjdk isn't linked onto PATH by default on macOS — surface that.
  if ! command -v java >/dev/null 2>&1; then
    log "note: openjdk installed but not on PATH. Follow brew's own"
    log "      'brew info openjdk' instructions to link it, or run:"
    log "      export PATH=\"\$(brew --prefix openjdk)/bin:\$PATH\""
  fi
}

install_termux() {
  pkg install -y nodejs python openjdk-21
  if ! command -v just >/dev/null 2>&1; then
    pkg install -y just 2>/dev/null || {
      log "note: 'just' isn't in the Termux repo on this device/arch."
      log "      Install via cargo instead: pkg install rust && cargo install just"
    }
  fi
}

install_linux() {
  if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update
    sudo apt-get install -y nodejs npm python3 default-jdk
  elif command -v dnf >/dev/null 2>&1; then
    sudo dnf install -y nodejs python3 java-latest-openjdk
  elif command -v pacman >/dev/null 2>&1; then
    sudo pacman -Sy --noconfirm nodejs npm python jdk-openjdk
  elif command -v zypper >/dev/null 2>&1; then
    sudo zypper install -y nodejs npm python3 java-17-openjdk
  else
    log "error: no supported package manager found (apt/dnf/pacman/zypper)."
    log "       Install node, python3, and a JDK manually, then re-run this"
    log "       script — it will still install 'just' below."
    exit 1
  fi

  if ! command -v just >/dev/null 2>&1; then
    log "installing just via its official install script (no universal distro package)..."
    curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to /usr/local/bin
  fi
}

main() {
  case "$(uname -s)" in
  Darwin)
    install_macos
    ;;
  Linux)
    if [ -n "${TERMUX_VERSION:-}" ] || [ -d /data/data/com.termux ]; then
      install_termux
    else
      install_linux
    fi
    ;;
  *)
    log "error: unsupported platform: $(uname -s)"
    log "       Install node, python3, java, and just manually."
    exit 1
    ;;
  esac

  log ""
  log "Done. Verify with: node --version && python3 --version && java -version && just --version"
}

main "$@"
