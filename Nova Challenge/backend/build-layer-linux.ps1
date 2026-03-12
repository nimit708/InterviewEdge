# Build Lambda Layer for Linux x86_64 platform
Write-Host "Building Lambda layer with Linux-compatible dependencies..." -ForegroundColor Green

# Clean up old package directory
if (Test-Path "package") {
    Remove-Item -Recurse -Force package
}

# Create package directory
New-Item -ItemType Directory -Path "package/python" -Force | Out-Null

# Install dependencies for Linux platform
Write-Host "Installing dependencies for Linux x86_64..." -ForegroundColor Yellow
pip install -r requirements.txt `
    --platform manylinux2014_x86_64 `
    --target package/python `
    --implementation cp `
    --python-version 3.11 `
    --only-binary=:all: `
    --upgrade

# Check if installation was successful
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error installing dependencies" -ForegroundColor Red
    exit 1
}

# Remove unnecessary files to reduce size
Write-Host "Cleaning up unnecessary files..." -ForegroundColor Yellow
Get-ChildItem -Path "package" -Include "*.pyc","*.pyo","__pycache__","*.dist-info" -Recurse | Remove-Item -Recurse -Force

# Create the layer zip
Write-Host "Creating layer.zip..." -ForegroundColor Yellow
if (Test-Path "layer.zip") {
    Remove-Item layer.zip
}

Compress-Archive -Path "package/*" -DestinationPath "layer.zip" -Force

Write-Host "Layer built successfully!" -ForegroundColor Green
Write-Host "Size: $((Get-Item layer.zip).Length / 1MB) MB" -ForegroundColor Cyan
