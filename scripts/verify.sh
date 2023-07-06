#!/bin/sh
set -eu
python -m pip check
python -m pytest tests -q
npm test --prefix frontend
npm run build --prefix frontend
git diff --check
