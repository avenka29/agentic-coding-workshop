# Native Windows PowerShell 5.1+ / PowerShell 7. No virtualenv activation needed.
[CmdletBinding()]
param(
    [ValidateSet('Setup', 'Dev', 'InstallTools')]
    [string]$Action = 'Setup',
    [string]$PythonBin = $env:PYTHON_BIN
)
$ErrorActionPreference = 'Stop'
$projectDir = Split-Path -Parent $PSScriptRoot
$versionProbe = 'import sys; sys.exit(0 if (3, 11) <= sys.version_info[:2] <= (3, 13) else 1)'

function Invoke-Checked {
    param([string]$Executable, [string[]]$Arguments)
    & $Executable @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code ${LASTEXITCODE}: $Executable $($Arguments -join ' ')"
    }
}

function Find-Python {
    $candidates = @()
    if ($PythonBin) {
        $candidates += @{ Executable = $PythonBin; Prefix = @() }
    } else {
        if (Get-Command py -ErrorAction SilentlyContinue) {
            foreach ($version in @('3.13', '3.12', '3.11')) {
                $candidates += @{ Executable = 'py'; Prefix = @("-$version") }
            }
        }
        foreach ($name in @('python3.13', 'python3.12', 'python3.11', 'python')) {
            if (Get-Command $name -ErrorAction SilentlyContinue) {
                $candidates += @{ Executable = $name; Prefix = @() }
            }
        }
    }
    foreach ($candidate in $candidates) {
        try {
            $prefixArgs = @($candidate.Prefix)
            $null = & $candidate.Executable @prefixArgs -c $versionProbe 2>$null
            if ($LASTEXITCODE -eq 0) { return $candidate }
        } catch { continue }
    }
    return $null
}

function Test-Node {
    if (!(Get-Command node -ErrorAction SilentlyContinue) -or !(Get-Command npm.cmd -ErrorAction SilentlyContinue)) {
        return $false
    }
    & node -e 'process.exit(Number(process.versions.node.split(".")[0]) >= 22 ? 0 : 1)'
    return ($LASTEXITCODE -eq 0)
}

Push-Location $projectDir
try {
    if ($Action -eq 'InstallTools') {
        if (!(Get-Command winget -ErrorAction SilentlyContinue)) {
            throw 'WinGet is missing. Use the official Node.js and Python 3.13 installers linked in docs/setup-guide.md.'
        }
        # This explicit action installs host tools; normal Setup never does.
        if (!(Test-Node)) {
            Invoke-Checked 'winget' @('install', '--exact', '--id', 'OpenJS.NodeJS.22', '--source', 'winget')
        }
        if (!(Find-Python)) {
            Invoke-Checked 'winget' @('install', '--exact', '--id', 'Python.Python.3.13', '--source', 'winget')
        }
        if (!(Get-Command git -ErrorAction SilentlyContinue)) {
            Invoke-Checked 'winget' @('install', '--exact', '--id', 'Git.Git', '--source', 'winget')
        }
        Write-Host 'Close and reopen PowerShell so new tools appear on PATH. Then run: .\scripts\windows.ps1 -Action Setup'
        exit 0
    }

    if (!(Test-Node)) {
        throw 'Node.js 22+ and npm are required. See docs/setup-guide.md or run -Action InstallTools, then reopen PowerShell.'
    }
    $venvPython = Join-Path $projectDir 'backend\.venv\Scripts\python.exe'
    if ($Action -eq 'Setup') {
        if (!(Get-Command git -ErrorAction SilentlyContinue)) {
            throw 'Git is required for workshop worktrees. Install Git for Windows or run -Action InstallTools.'
        }
        $python = Find-Python
        if (!$python) {
            throw 'Python 3.11-3.13 is required. Use -PythonBin C:\path\to\python.exe or install Python 3.13; see docs/setup-guide.md.'
        }
        if (Test-Path 'backend\.venv') {
            if (!(Test-Path $venvPython)) {
                throw 'backend/.venv belongs to another platform or is incomplete. Move it aside; it has been preserved.'
            }
            Invoke-Checked $venvPython @('-c', $versionProbe)
        } else {
            Invoke-Checked $python.Executable (@($python.Prefix) + @('-m', 'venv', 'backend/.venv'))
        }
        Invoke-Checked $venvPython @('-m', 'pip', 'install', '-r', 'backend/requirements.txt')
        if (Test-Path 'frontend/package-lock.json') {
            Invoke-Checked 'npm.cmd' @('--prefix', 'frontend', 'ci')
        } else {
            Invoke-Checked 'npm.cmd' @('--prefix', 'frontend', 'install')
        }
        Push-Location 'backend'
        try { Invoke-Checked $venvPython @('-m', 'pytest', '-q') } finally { Pop-Location }
        Invoke-Checked 'npm.cmd' @('--prefix', 'frontend', 'test')
        Invoke-Checked 'npm.cmd' @('--prefix', 'frontend', 'run', 'build')
        Write-Host 'Setup and checks passed. Start with: .\scripts\windows.ps1 -Action Dev'
    } else {
        if (!(Test-Path $venvPython) -or !(Test-Path 'frontend/node_modules/vite/bin/vite.js')) {
            throw 'Dependencies are missing. Run .\scripts\windows.ps1 -Action Setup first.'
        }
        Invoke-Checked $venvPython @('-c', 'import fastapi, uvicorn')
        foreach ($port in @(8000, 5173)) {
            $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, $port)
            try { $listener.Start() } catch { throw "Port $port is occupied. Stop its existing service before starting this checkout." } finally { $listener.Stop() }
        }
        $backend = $null
        $frontend = $null
        try {
            $backend = Start-Process -FilePath $venvPython -ArgumentList @('-m', 'uvicorn', 'app:app', '--reload', '--host', '127.0.0.1', '--port', '8000') -WorkingDirectory (Join-Path $projectDir 'backend') -NoNewWindow -PassThru
            $frontend = Start-Process -FilePath (Get-Command node).Source -ArgumentList @('node_modules/vite/bin/vite.js') -WorkingDirectory (Join-Path $projectDir 'frontend') -NoNewWindow -PassThru
            Write-Host 'Starting app: http://127.0.0.1:5173 | API docs: http://127.0.0.1:8000/docs'
            Write-Host 'Wait for startup messages. Press Ctrl-C to stop both services.'
            while (!$backend.HasExited -and !$frontend.HasExited) {
                Start-Sleep -Seconds 1
                $backend.Refresh()
                $frontend.Refresh()
            }
            $ended = if ($backend.HasExited) { $backend } else { $frontend }
            if ($ended.ExitCode -ne 0) { throw "A service exited with code $($ended.ExitCode). Check its startup output." }
        } finally {
            # Stop only the process trees launched by this script, including reload workers.
            foreach ($service in @($backend, $frontend)) {
                if ($null -ne $service) {
                    $service.Refresh()
                    if (!$service.HasExited) {
                        try { & taskkill.exe /PID $service.Id /T /F 2>$null | Out-Null }
                        catch { Write-Warning "Unable to stop service PID $($service.Id). Check that service manually." }
                    }
                }
            }
        }
    }
} finally {
    Pop-Location
}
