# autojs6-typescript — TypeScript for AutoJs6's Rhino runtime.
# Requires: node (tsc), python3, java (only for rhino-* recipes), just.
# `just install-deps` installs all of these on macOS / major Linux / Termux.

# Show available recipes.
default:
    @just --list

# Install system dependencies (node, python3, java, just) for this platform.
install-deps:
    bash tools/install-deps.sh

# Install TypeScript.
install:
    npm install

# Compile every .ts file (src/, examples/) to .js, formatted.
build:
    npx tsc -p tsconfig.json
    npx biome format --write src examples types
    npx biome check --write src examples types

# Verify 1:1 .ts/.js mapping — a missing .js means `just build` wasn't run.
check-build:
    python3 tools/check_build.py src examples types

# Locate an AutoJs6 fork's bundled Rhino jar (pass a source checkout dir or a .jar path).
find-rhino-jar path:
    python3 tools/find_rhino_jar.py {{ path }}

# Print a Rhino jar's runtime version string (paste into your own main.ts).
rhino-version jar:
    python3 tools/print_rhino_version.py {{ jar }}

# Run the clean example through a real Rhino build — expect every file to parse.
check-clean jar: build
    python3 tools/rhino_check.py {{ jar }} $(find examples/clean -name "*.js")

# Run every broken example through a real Rhino build and report each error
# — WITHOUT fixing anything. This documents what breaks and why; see each
# examples/broken/*/README.md for the fix.
find-errors jar: build
    python3 tools/find_errors.py {{ jar }} examples/broken

# Static checks (no jar/device needed): for...of syntax + duplicate require()
# binding names, scanned across the clean example's compiled output.
lint-rhino: build
    python3 tools/check_require_bindings.py examples/clean

# Full test suite: build, static checks, and the real Rhino checks against
# both the clean and broken examples (pass your fork's jar — see
# find-rhino-jar).
test jar: build lint-rhino
    just check-clean {{ jar }}
    just find-errors {{ jar }}

# Format everything (TS via biome, Python via ruff).
fmt:
    npx biome format --write src examples types
    ruff format tools/

# Lint everything.
lint:
    npx biome check src examples types
    ruff check tools/
    mypy tools/

# Run pre-commit across the whole repo.
precommit:
    pre-commit run --all-files
