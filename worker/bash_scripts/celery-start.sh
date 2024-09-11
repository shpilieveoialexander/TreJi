#! /usr/bin/env bash
set -e

celery -A service.tasks worker  -l info -Q main-queue -E
