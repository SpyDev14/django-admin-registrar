param(
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidateSet("public", "test")]
    [string]$index,

    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$arguments
)

# uvIndex can bu null for use default index
$targets = @{
    public = @{ uvIndex = $null;  tokenVar = "UV_PUBLISH_TOKEN_FOR_PUBLIC" }
    test   = @{ uvIndex = "test"; tokenVar = "UV_PUBLISH_TOKEN_FOR_TEST"   }
}

$target = $targets[$index]

$token = [Environment]::GetEnvironmentVariable($target.tokenVar)
if (-not $token) { $token = [Environment]::GetEnvironmentVariable($target.tokenVar, "User") }
if (-not $token) {
    Write-Error "Environment variable '$($target.tokenVar)' is not set."
    exit 1
}

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Error "'uv' not found in PATH."
    exit 1
}

$uvArgs = @()
if ($target.uvIndex) { $uvArgs += @("--index", $target.uvIndex) }
if ($arguments)      { $uvArgs += $arguments }

$previousToken = $env:UV_PUBLISH_TOKEN
$env:UV_PUBLISH_TOKEN = $token

$exitCode = 0
try {
    & uv publish @uvArgs
    $exitCode = $LASTEXITCODE
}
finally {
    $env:UV_PUBLISH_TOKEN = $previousToken
}

exit $exitCode
