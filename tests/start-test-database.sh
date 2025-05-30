#!/bin/bash
# Script to start test database for oc_ocdm

# Get the absolute path of the current directory
CURRENT_DIR="$(pwd)"

# Remove test database directory if it exists and create a new one
TEST_DB_DIR="${CURRENT_DIR}/tests/test_db"
if [ -d "${TEST_DB_DIR}" ]; then
    echo "Removing existing test database directory..."
    rm -rf "${TEST_DB_DIR}"
fi
mkdir -p "${TEST_DB_DIR}"

# Copy the custom virtuoso.ini to the test database directory
cp "${CURRENT_DIR}/tests/virtuoso.ini" "${TEST_DB_DIR}/virtuoso.ini"

# Check if container already exists and remove it if it does
if [ "$(docker ps -a -q -f name=test-virtuoso-ocdm)" ]; then
    echo "Removing existing test-virtuoso-ocdm container and its volumes..."
    docker rm -f -v test-virtuoso-ocdm
fi

# Start Virtuoso database with custom configuration
echo "Starting test-virtuoso-ocdm container..."
docker run -d --name test-virtuoso-ocdm \
  -p 1104:1104 \
  -p 8804:8804 \
  -e DBA_PASSWORD=dba \
  -e SPARQL_UPDATE=true \
  -v "${TEST_DB_DIR}:/database" \
  openlink/virtuoso-opensource-7:latest

# Wait for database to be ready
echo "Waiting for test database to start..."
sleep 30
echo "Test database should be ready now."

# Set permissions for the 'nobody' user
echo "Setting permissions for the 'nobody' user..."
docker exec test-virtuoso-ocdm /opt/virtuoso-opensource/bin/isql -S 1104 -U dba -P dba exec="DB.DBA.RDF_DEFAULT_USER_PERMS_SET ('nobody', 7);"

# Grant SPARQL_UPDATE role to SPARQL user
echo "Granting SPARQL_UPDATE role..."
docker exec test-virtuoso-ocdm /opt/virtuoso-opensource/bin/isql -S 1104 -U dba -P dba exec="DB.DBA.USER_GRANT_ROLE ('SPARQL', 'SPARQL_UPDATE');"

echo "Setup completed."
echo "Virtuoso SPARQL endpoint: http://localhost:8804/sparql"
echo "Virtuoso Conductor: http://localhost:8804/conductor" 