#! /usr/bin/env bash
set -e

celery -A service.tasks worker --beat -l info -Q main-queue,schedule-queue,mail-queue -E
