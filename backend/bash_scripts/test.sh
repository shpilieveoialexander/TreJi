#!/usr/bin/env bash

set -e
set -x

# Clear console history
clear

# Run tests
pytest /backend/tests/ "${@}"
