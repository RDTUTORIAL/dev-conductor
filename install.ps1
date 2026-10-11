<#
Install the dev-conductor skill for Claude Code and/or Codex-style agents on Windows.

  .\install.ps1                      # user-wide, both agents
  .\install.ps1 -Agent claude        # Claude Code only
  .\install.ps1 -Agent codex         # Codex / ~/.agents/skills only
  .\install.ps1 -Project C:\code\app # into the project's .claude\skills and .agents\skills
  .\install.ps1 -Project . -AgentsMd # also copy templates\AGENTS.md if the project has none
  .\install.ps1 -Force               # replace an existing install (old one goes to ..\skill-backups)
  .\install.ps1 -WithCompanions core,frontend   # also install companion skills ('all' for every pack)
  .\install.ps1 -WithCompanions all -Yes        # without the confirmation prompt
#>
param(
  [ValidateSet("both", "claude", "codex")] [string] $Agent = "both",
  [string] $Project = "",
  [switch] $AgentsMd,
  [switch] $Force,
  [string] $WithCompanions = "",
  [switch] $Yes
)
$ErrorActionPreference = "Stop"

$Name = "dev-conductor"
$SrcRoot = $PSScriptRoot
$Src = Join-Path $SrcRoot "skills\$Name"
if (-not (Test-Path (Join-Path $Src "SKILL.md"))) { throw "cannot find $Src\SKILL.md" }

if ($Project) {
  $Base = (Resolve-Path $Project).Path
  $ClaudeDir = Join-Path $Base ".claude\skills"
  $CodexDir = Join-Path $Base ".agents\skills"
} else {
  $ClaudeHome = if ($env:CLAUDE_CONFIG_DIR) { $env:CLAUDE_CONFIG_DIR } else { Join-Path $HOME ".claude" }
  $ClaudeDir = Join-Path $ClaudeHome "skills"
  $CodexDir = Join-Path $HOME ".agents\skills"
}

function Install-To([string] $Dir) {
  $Dest = Join-Path $Dir $Name
  New-Item -ItemType Directory -Force -Path $Dir | Out-Null
  if (Test-Path $Dest) {
    if (-not $Force) { Write-Host "skip: $Dest exists (use -Force to replace)"; return }
    # Back up outside the skills folder, or the agent would load the backup as a second skill.
    $BackupDir = Join-Path (Split-Path $Dir -Parent) "skill-backups"
    New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null
    $Backup = Join-Path $BackupDir "$Name.$(Get-Date -Format yyyyMMddHHmmss)"
    Move-Item $Dest $Backup
    Write-Host "moved old install to $Backup"
  }
  Copy-Item -Recurse $Src $Dest
  Get-ChildItem -Path $Dest -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
  Write-Host "installed: $Dest"
}

if ($Agent -in @("both", "claude")) { Install-To $ClaudeDir }
if ($Agent -in @("both", "codex")) { Install-To $CodexDir }

if ($AgentsMd) {
  if (-not $Project) { Write-Warning "-AgentsMd needs -Project" }
  elseif (Test-Path (Join-Path $Base "AGENTS.md")) { Write-Host "skip: AGENTS.md exists; merge templates\AGENTS.md by hand" }
  else {
    Copy-Item (Join-Path $SrcRoot "templates\AGENTS.md") (Join-Path $Base "AGENTS.md")
    Write-Host "copied AGENTS.md template; fill in section 2 (repo facts)"
  }
}

$Py = Get-Command py -ErrorAction SilentlyContinue
if ($Py) { & py -3 -I (Join-Path $Src "scripts\validate.py") | Out-Null; if ($LASTEXITCODE -eq 0) { Write-Host "self-check: ok" } }
elseif (Get-Command python -ErrorAction SilentlyContinue) { & python -I (Join-Path $Src "scripts\validate.py") | Out-Null; if ($LASTEXITCODE -eq 0) { Write-Host "self-check: ok" } }
else { Write-Host "note: Python not found; the skill still works, but its helper scripts will be skipped" }
if ($WithCompanions) {
  $PyCmd = if (Get-Command py -ErrorAction SilentlyContinue) { @("py", "-3") } elseif (Get-Command python -ErrorAction SilentlyContinue) { @("python") } else { $null }
  if (-not $PyCmd) { throw "-WithCompanions needs Python; see README for installing companions by hand" }
  $CompArgs = @((Join-Path $SrcRoot "install_companions.py"))
  if ($WithCompanions -eq "all") { $CompArgs += "--all" } else { $CompArgs += @("--packs", $WithCompanions) }
  if ($Project) { $CompArgs += @("--project", $Base, "--repo", $Base) }
  $CompArgs += @("--agent", $Agent)
  if ($Yes) { $CompArgs += "--yes" }
  $Exe = $PyCmd[0]; $Rest = @($PyCmd | Select-Object -Skip 1) + $CompArgs
  & $Exe @Rest
  if ($LASTEXITCODE -ne 0) { throw "companion install failed" }
}
Write-Host "Restart your agent session so it picks up the skill."
