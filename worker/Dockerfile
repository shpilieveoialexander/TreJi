# Build image from base dockerfile image
FROM base_dockerfile as build_dockerfile

# Final build
FROM python:3.11-slim

# Remove apt chache
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Set workdir in future container
WORKDIR /backend/

# Copy dependencies from build image to final image
COPY --from=build_dockerfile /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=build_dockerfile /usr/local/bin/ /usr/local/bin/

# Copy code source to container
COPY ./ /backend/

# Find all bash scripts and add permision for executing
RUN find . -type f -iname "*.sh" -exec chmod +x {} \;

# Open backend port
EXPOSE ${WORKER_PORT}

ENV PYTHONPATH=.

# Run script for starting project
CMD ["/backend/bash_scripts/celery-start.sh"]

