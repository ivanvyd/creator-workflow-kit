param(
    [switch]$SkipChromium
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Venv = Join-Path $Root ".venv"
if (-not (Test-Path -LiteralPath $Venv)) {
    python -m venv $Venv
    if ($LASTEXITCODE -ne 0) { throw "venv creation failed with exit code $LASTEXITCODE" }
}
$Python = Join-Path $Venv "Scripts\python.exe"
& $Python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "pip upgrade failed with exit code $LASTEXITCODE" }
& $Python -m pip install -e "${Root}[dev]"
if ($LASTEXITCODE -ne 0) { throw "editable install failed with exit code $LASTEXITCODE" }
if (-not $SkipChromium) {
    & $Python -m playwright install chromium
    if ($LASTEXITCODE -ne 0) { throw "Chromium install failed with exit code $LASTEXITCODE" }
}
if (-not (Test-Path -LiteralPath (Join-Path $Root "config.toml"))) {
    Copy-Item -LiteralPath (Join-Path $Root "config.example.toml") -Destination (Join-Path $Root "config.toml")
    Write-Host "Created config.toml from the template. It contains environment-variable names only."
}
$ClaudeSkills = Join-Path $Root ".claude\skills"
$ExpectedSkills = (Resolve-Path -LiteralPath (Join-Path $Root ".agents\skills")).Path
if (Test-Path -LiteralPath $ClaudeSkills) {
    $LinkItem = Get-Item -LiteralPath $ClaudeSkills -Force
    if ($LinkItem.LinkType -ne "Junction" -or [string]$LinkItem.Target -ne $ExpectedSkills) {
        Write-Warning "Refusing to replace existing $ClaudeSkills"
    }
} else {
    New-Item -ItemType Directory -Force -Path (Join-Path $Root ".claude") | Out-Null
    New-Item -ItemType Junction -Path $ClaudeSkills -Target $ExpectedSkills | Out-Null
}
Write-Host "Ready: & .\.venv\Scripts\python -m creator_kit doctor"
