[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [Parameter()]
    [string]$Destination = 'C:\src\gcpl-mps',

    [Parameter()]
    [string]$Branch = 'mps/materialization'
)

$ErrorActionPreference = 'Stop'
$source = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$destinationFull = [System.IO.Path]::GetFullPath($Destination)

if ($destinationFull -match '\s') {
    throw "Destination must be space-free: $destinationFull"
}
if ($destinationFull -like '*OneDrive*') {
    throw "Destination must not be inside OneDrive: $destinationFull"
}
if (Test-Path -LiteralPath $destinationFull) {
    throw "Destination already exists; refusing to overwrite it: $destinationFull"
}

$status = & git -C $source status --porcelain=v1
if ($LASTEXITCODE -ne 0) {
    throw 'Unable to inspect the source repository.'
}
if ($status) {
    throw 'The source worktree is not clean. Commit or stash all changes before creating the MPS worktree.'
}

$sourceHead = (& git -C $source rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0) {
    throw 'Unable to resolve the source commit.'
}
$sourceCommon = (& git -C $source rev-parse --path-format=absolute --git-common-dir).Trim()
if ($LASTEXITCODE -ne 0) {
    throw 'Unable to resolve the controlling Git common directory.'
}
$parent = Split-Path -Parent $destinationFull

& git -C $source show-ref --verify --quiet "refs/heads/$Branch"
$branchExists = $LASTEXITCODE -eq 0
$action = if ($branchExists) {
    "Create managed worktree for existing branch $Branch from $source"
}
else {
    "Create managed worktree and branch $Branch from $sourceHead"
}

if ($PSCmdlet.ShouldProcess($destinationFull, $action)) {
    if (-not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent | Out-Null
    }
    if ($branchExists) {
        & git -C $source worktree add -- $destinationFull $Branch
    }
    else {
        & git -C $source worktree add -b $Branch -- $destinationFull $sourceHead
    }
    if ($LASTEXITCODE -ne 0) {
        throw 'Git worktree creation failed.'
    }
    $destinationHead = (& git -C $destinationFull rev-parse HEAD).Trim()
    $destinationCommon = (& git -C $destinationFull rev-parse --path-format=absolute --git-common-dir).Trim()
    if ($destinationHead -ne $sourceHead) {
        throw "Destination commit does not match source ($destinationHead versus $sourceHead)."
    }
    if ([System.IO.Path]::GetFullPath($destinationCommon) -ne [System.IO.Path]::GetFullPath($sourceCommon)) {
        throw 'Destination does not share the controlling Git common directory.'
    }
    & git -C $source worktree list --porcelain
    if ($LASTEXITCODE -ne 0) {
        throw 'Unable to verify the registered worktree.'
    }
    Write-Output "Managed MPS worktree verified at $destinationFull on branch $Branch"
    Write-Output 'The original checkout was not deleted. Open only the managed worktree in MPS.'
}
