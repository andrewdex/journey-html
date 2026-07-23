#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $0 /absolute/output/directory" >&2
}

if [[ $# -ne 1 ]]; then
  usage
  exit 64
fi

destination=$1

if [[ $destination != /* ]]; then
  echo "Error: destination must be an absolute path." >&2
  exit 64
fi

if [[ -e $destination ]]; then
  echo "Error: destination already exists; refusing to overwrite it." >&2
  exit 73
fi

mkdir -p -- "$destination"
printf 'Created journey workspace: %s\n' "$destination"
