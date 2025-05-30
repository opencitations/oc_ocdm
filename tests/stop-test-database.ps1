# PowerShell script to stop test database for oc_ocdm

# Stop and remove the test database container
if (docker ps -a --format "{{.Names}}" | Select-String -Pattern "^test-virtuoso-ocdm$") {
    Write-Host "Stopping and removing test-virtuoso-ocdm container..."
    docker stop test-virtuoso-ocdm
    docker rm test-virtuoso-ocdm
}

Write-Host "Test database stopped and removed." 