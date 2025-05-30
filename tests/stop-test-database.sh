#!/bin/bash
# Script to stop test database for oc_ocdm

# Get the absolute path of the current directory
CURRENT_DIR="$(pwd)"
TEST_DB_DIR="${CURRENT_DIR}/tests/test_db"

# Stop and remove the test database container and its volumes
if [ "$(docker ps -a -q -f name=test-virtuoso-ocdm)" ]; then
    echo "Stopping and removing test-virtuoso-ocdm container and its volumes..."
    docker stop test-virtuoso-ocdm
    docker rm -v test-virtuoso-ocdm
else
    echo "No test-virtuoso-ocdm container found."
fi

# Remove test database directory if it exists
if [ -d "${TEST_DB_DIR}" ]; then
    echo "Removing test database directory..."
    rm -rf "${TEST_DB_DIR}"
else
    echo "No test database directory found at ${TEST_DB_DIR}"
fi

echo "Test database cleanup completed." 