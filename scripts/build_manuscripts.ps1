param([string]$OutputDirectory)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
if (-not $OutputDirectory) {
    $OutputDirectory = Join-Path ([IO.Path]::GetTempPath()) ('ivqr-build-' + [guid]::NewGuid())
}
$buildRoot = [IO.Path]::GetFullPath($OutputDirectory)
if ($buildRoot.StartsWith($repoRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase) -or $buildRoot -eq $repoRoot) {
    throw 'Keep build products outside the repository.'
}
if (Test-Path -LiteralPath $buildRoot) { throw 'Use a new output directory; existing builds are not overwritten.' }
foreach ($toolName in @('pdflatex', 'biber')) {
    if (-not (Get-Command $toolName -ErrorAction SilentlyContinue)) { throw "Required tool missing: $toolName" }
}
New-Item -ItemType Directory -Path $buildRoot | Out-Null
$oldLocale = $env:LC_ALL
$oldLanguage = $env:LANG
$env:LC_ALL = 'C'
$env:LANG = 'C'
Push-Location (Join-Path $repoRoot 'article')
try {
    # Windows PowerShell treats native stderr as an error record. Capture it,
    # then use the native exit code to decide whether the build failed.
    $ErrorActionPreference = 'Continue'
    foreach ($entry in @('main', 'review')) {
        $entryOutput = Join-Path $buildRoot $entry
        New-Item -ItemType Directory -Path $entryOutput | Out-Null
        & pdflatex -no-shell-escape -interaction=nonstopmode -halt-on-error -recorder "-output-directory=$entryOutput" "$entry.tex" *> (Join-Path $entryOutput 'pass1-console.txt')
        if ($LASTEXITCODE -ne 0) { throw "First LaTeX pass failed: $entry; see $entryOutput" }
        & biber --input-directory $entryOutput --output-directory $entryOutput $entry *> (Join-Path $entryOutput 'biber-console.txt')
        if ($LASTEXITCODE -ne 0) { throw "Biber failed: $entry; see $entryOutput" }
        foreach ($pass in @(2, 3)) {
            & pdflatex -no-shell-escape -interaction=nonstopmode -halt-on-error -recorder "-output-directory=$entryOutput" "$entry.tex" *> (Join-Path $entryOutput "pass$pass-console.txt")
            if ($LASTEXITCODE -ne 0) { throw "LaTeX pass $pass failed: $entry; see $entryOutput" }
        }
        Write-Output (Join-Path $entryOutput "$entry.pdf")
    }
} finally {
    Pop-Location
    $env:LC_ALL = $oldLocale
    $env:LANG = $oldLanguage
    $ErrorActionPreference = 'Stop'
}
