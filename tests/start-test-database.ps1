# PowerShell script to start test database for oc_ocdm

# Get the absolute path of the current directory
$CURRENT_DIR = (Get-Location).Path

# Create test database directory if it doesn't exist
$dbPath = Join-Path -Path $CURRENT_DIR -ChildPath "tests\test_db"

if (Test-Path -Path $dbPath) {
    Write-Host "Removing existing test database directory..."
    Remove-Item -Path $dbPath -Recurse -Force
}
Write-Host "Creating database directory..."
New-Item -Path $dbPath -ItemType Directory -Force | Out-Null

# Copy the custom virtuoso.ini to the test database directory
$virtuosoIniSource = Join-Path -Path $CURRENT_DIR -ChildPath "tests\virtuoso.ini"
$virtuosoIniDest = Join-Path -Path $dbPath -ChildPath "virtuoso.ini"
Copy-Item -Path $virtuosoIniSource -Destination $virtuosoIniDest

# Check if container already exists and remove it if it does
if (docker ps -a --format "{{.Names}}" | Select-String -Pattern "^test-virtuoso-ocdm$") {
    Write-Host "Removing existing test-virtuoso-ocdm container..."
    docker rm -f test-virtuoso-ocdm
}

# Start Virtuoso database with custom configuration
Write-Host "Starting test-virtuoso-ocdm container..."
docker run -d --name test-virtuoso-ocdm `
  -p 1104:1104 `
  -p 8804:8804 `
  -e DBA_PASSWORD=dba `
  -e SPARQL_UPDATE=true `
  -v "${dbPath}:/database" `
  openlink/virtuoso-opensource-7:latest

# Wait for database to be ready
Write-Host "Waiting for test database to start..."
Start-Sleep -Seconds 30
Write-Host "Test database should be ready now."

# Set permissions for the 'nobody' user
Write-Host "Setting permissions for the 'nobody' user..."
docker exec test-virtuoso-ocdm /opt/virtuoso-opensource/bin/isql -S 1104 -U dba -P dba exec="DB.DBA.RDF_DEFAULT_USER_PERMS_SET ('nobody', 7);"

# Grant SPARQL_UPDATE role to SPARQL user
Write-Host "Granting SPARQL_UPDATE role..."
docker exec test-virtuoso-ocdm /opt/virtuoso-opensource/bin/isql -S 1104 -U dba -P dba exec="DB.DBA.USER_GRANT_ROLE ('SPARQL', 'SPARQL_UPDATE');"

Write-Host "Setup completed."
Write-Host "Virtuoso SPARQL endpoint: http://localhost:8804/sparql"
Write-Host "Virtuoso Conductor: http://localhost:8804/conductor" 