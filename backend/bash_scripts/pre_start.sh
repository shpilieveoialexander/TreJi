#! /usr/bin/env sh

# Create DB
python /backend/db/init_db.py

# Run migrations
alembic upgrade head


echo pre_start.sh has worked
