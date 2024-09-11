#!/usr/bin/env bash

set -e
set -x

# Clear console history
clear

# Run pytests and create .coverage with reports
coverage run -m pytest

# Convert .coverage to coverage.json
coverage json

# Remove old SVG and .coverage
rm -f coverage.svg .coverage

# Generate coverage badge from .coverage
anybadge -l backend_coverage -v $(python -c "import sys, ujson; print(ujson.load(open('/backend/coverage.json'))['totals']['percent_covered_display'])")% -f coverage.svg

# Remove coverage.json
rm -f coverage.json