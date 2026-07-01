$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonPath = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$PidFile = Join-Path $ProjectRoot ".uvicorn.pid"
$Port = 8000

function Get-ListeningProcessIds {
    $ids = @()

    try {
        $ids += Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction Stop |
            Select-Object -ExpandProperty OwningProcess -Unique
    }
    catch {
        $lines = netstat.exe -ano
        foreach ($line in $lines) {
            if ($line -match "^\s*TCP\s+\S+:$Port\s+\S+\s+LISTENING\s+(\d+)\s*$") {
                $ids += [int]$matches[1]
            }
        }
    }

    @($ids | Where-Object { $_ } | Select-Object -Unique)
}

function Get-ProcessTreeIds {
    param([int]$RootPid)

    $ids = @($RootPid)
    $children = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
        Where-Object { $_.ParentProcessId -eq $RootPid }

    foreach ($child in $children) {
        $ids += Get-ProcessTreeIds -RootPid ([int]$child.ProcessId)
    }

    @($ids | Select-Object -Unique)
}

function Get-BackendProcessIds {
    $ids = @(Get-ListeningProcessIds)

    if (Test-Path $PidFile) {
        $savedPid = Get-Content -Path $PidFile -ErrorAction SilentlyContinue
        if ($savedPid -match "^\d+$") {
            $ids += [int]$savedPid
        }
    }

    $normalizedRoot = $ProjectRoot.ToLowerInvariant()

    $matches = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
        Where-Object {
            $cmd = if ($_.CommandLine) { $_.CommandLine.ToLowerInvariant() } else { "" }
            $cmd.Contains("uvicorn") -and
            $cmd.Contains("main:app") -and
            $cmd.Contains($normalizedRoot)
        }

    foreach ($p in $matches) {
        $ids += [int]$p.ProcessId
        if ($p.ParentProcessId) {
            $ids += [int]$p.ParentProcessId
        }

        $ids += Get-ProcessTreeIds -RootPid ([int]$p.ProcessId)
    }

    foreach ($id in @($ids)) {
        $ids += Get-ProcessTreeIds -RootPid ([int]$id)
    }

    @($ids | Where-Object { $_ } | Select-Object -Unique)
}

function Test-ProcessRunning {
    param([int]$ProcessId)

    try {
        Get-Process -Id $ProcessId -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

function Stop-BackendProcess {
    param([int]$ProcessId)

    if (-not (Test-ProcessRunning -ProcessId $ProcessId)) {
        return
    }

    try {
        taskkill.exe /PID $ProcessId /T /F | Out-Null
    }
    catch {}

    Start-Sleep -Milliseconds 300

    if (Test-ProcessRunning -ProcessId $ProcessId) {
        try {
            Stop-Process -Id $ProcessId -Force -ErrorAction SilentlyContinue
        }
        catch {}
    }
}

function Start-BackendService {
    $running = @(Get-ListeningProcessIds)

    if ($running.Count -gt 0) {
        Write-Host "El servicio ya esta encendido en http://127.0.0.1:$Port"
        Write-Host "PID: $($running -join ', ')"
        return
    }

    if (-not (Test-Path $PythonPath)) {
        Write-Host "No se encontro el entorno virtual en .venv."
        return
    }

    $arguments = @(
        "-m", "uvicorn", "main:app",
        "--host", "127.0.0.1",
        "--port", "$Port",
        "--reload",
        "--reload-dir", $ProjectRoot
    )

    $process = Start-Process `
        -FilePath $PythonPath `
        -ArgumentList $arguments `
        -WorkingDirectory $ProjectRoot `
        -WindowStyle Hidden `
        -PassThru

    $process.Id | Set-Content -Path $PidFile -Encoding ascii

    Start-Sleep -Seconds 2

    $running = @(Get-ListeningProcessIds)

    if ($running.Count -gt 0) {
        Write-Host "Servicio encendido: http://127.0.0.1:$Port"
        Write-Host "PID: $($running -join ', ')"
    }
    else {
        Write-Host "Se intento iniciar el servicio, pero el puerto $Port no esta escuchando."
    }
}

function Stop-BackendService {
    $ids = @(Get-BackendProcessIds)

    if ($ids.Count -eq 0) {
        Write-Host "El servicio no esta encendido en el puerto $Port."
        if (Test-Path $PidFile) {
            Remove-Item -Path $PidFile -Force
        }
        return
    }

    foreach ($id in $ids | Sort-Object -Descending) {
        Stop-BackendProcess -ProcessId ([int]$id)
    }

    Start-Sleep -Seconds 1

    $remaining = @(Get-ListeningProcessIds)

    if ($remaining.Count -gt 0) {
        foreach ($id in $remaining) {
            Stop-BackendProcess -ProcessId ([int]$id)
        }
    }

    Start-Sleep -Milliseconds 500

    $remaining = @(Get-ListeningProcessIds)

    if ($remaining.Count -gt 0) {
        Write-Host "No se pudo detener el puerto $Port. PID activo: $($remaining -join ', ')"
    }
    else {
        Write-Host "Servicio detenido."
    }

    if (Test-Path $PidFile) {
        Remove-Item -Path $PidFile -Force
    }
}

function Main {
    Clear-Host
    Write-Host ""
    Write-Host "Backend LLM"
    Write-Host "1. Start"
    Write-Host "2. Stop"
    Write-Host ""

    $option = (Read-Host "Elige una opcion").Trim()

    switch ($option) {
        "1" { Start-BackendService }
        "2" { Stop-BackendService }
        default { Write-Host "Opcion invalida." }
    }
}

Main