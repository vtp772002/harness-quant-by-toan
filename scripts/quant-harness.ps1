# Cross-platform adapter: policy lives in the Rust control plane.
[CmdletBinding()]
param(
    [Parameter(Position = 0)] [string] $Command = "help",
    [Parameter(ValueFromRemainingArguments = $true)] [string[]] $Arguments
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Cli = Join-Path $Root "crates/harness-cli/Cargo.toml"
$Forwarded = @($Command) + @($Arguments) + @("--root", $Root)
foreach ($Candidate in @(
    (Join-Path $Root "scripts/bin/quant-harness.exe"),
    (Join-Path $Root "scripts/bin/quant-harness")
)) {
    if (Test-Path $Candidate) {
        & $Candidate @Forwarded
        exit $LASTEXITCODE
    }
}
& cargo run --quiet --manifest-path $Cli -- @Forwarded
exit $LASTEXITCODE
