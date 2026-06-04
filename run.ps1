$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonPath = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$PidFile = Join-Path $ProjectRoot ".uvicorn.pid"
$Port = 8000

function Get-ListeningProcessIds {
    $processIds = @()

    try {
        $processIds += Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction Stop |
            Select-Object -ExpandProperty OwningProcess -Unique
    }
    catch {
        try {
            $netstatLines = netstat.exe -ano
            foreach ($line in $netstatLines) {
                if ($line -match "^\s*TCP\s+\S+:$Port\s+\S+\s+LISTENING\s+(\d+)\s*$") {
                    $processIds += [int]$matches[1]
                }
            }
        }
        catch {
            @()
        }
    }

    @($processIds | Where-Object { $_ } | Select-Object -Unique)
}

function Get-BackendProcessIds {
    $processIds = @(Get-ListeningProcessIds)

    if (Test-Path $PidFile) {
        $savedPid = Get-Content -Path $PidFile -ErrorAction SilentlyContinue
        if ($savedPid) {
            $processIds += $savedPid
        }
    }

    try {
        $normalizedRoot = $ProjectRoot.ToLowerInvariant()
        $backendProcesses = Get-CimInstance Win32_Process |
            Where-Object {
                $commandLine = if ($_.CommandLine) { $_.CommandLine.ToLowerInvariant() } else { "" }
                $commandLine.Contains("uvicorn") -and
                    $commandLine.Contains("main:app") -and
                    $commandLine.Contains($normalizedRoot)
            }

        foreach ($backendProcess in $backendProcesses) {
            $processIds += $backendProcess.ProcessId
            if ($backendProcess.ParentProcessId) {
                $processIds += $backendProcess.ParentProcessId
            }
        }
    }
    catch {
        # La deteccion por puerto y pid file sigue funcionando si CIM no esta disponible.
    }

    @($processIds | Where-Object { $_ } | Select-Object -Unique)
}

function Test-ProcessRunning {
    param([int]$ProcessId)

    try {
        Get-Process -Id $ProcessId -ErrorAction Stop | Out-Null
        $true
    }
    catch {
        $false
    }
}

function Stop-BackendProcess {
    param([int]$ProcessId)

    taskkill.exe /PID $ProcessId /T /F | Out-Null

    $stillListening = @(Get-ListeningProcessIds) -contains $ProcessId
    if ($stillListening -or (Test-ProcessRunning -ProcessId $ProcessId)) {
        try {
            Stop-Process -Id $ProcessId -Force -ErrorAction Stop
        }
        catch {
            # Se reporta abajo si sigue activo.
        }
    }

    Start-Sleep -Milliseconds 250

    $stillListening = @(Get-ListeningProcessIds) -contains $ProcessId
    if ($stillListening) {
        Write-Host "No se pudo detener el proceso ${ProcessId}."
    }
    else {
        Write-Host "Proceso detenido: $ProcessId"
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
        Write-Host "Crea el entorno e instala dependencias antes de iniciar el servicio."
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
        Write-Host "Se intento iniciar el servicio, pero el puerto $Port aun no esta escuchando."
        Write-Host "Revisa la salida del proceso o ejecuta: .\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port $Port --reload"
    }
}

function Stop-BackendService {
    $processIds = @(Get-BackendProcessIds)
    if ($processIds.Count -eq 0) {
        Write-Host "El servicio no esta encendido en el puerto $Port."
        return
    }

    foreach ($processId in $processIds) {
        Stop-BackendProcess -ProcessId $processId
    }

    $remaining = @(Get-ListeningProcessIds)
    if ($remaining.Count -gt 0) {
        Write-Host "El puerto $Port sigue ocupado por PID: $($remaining -join ', ')"
    }
    else {
        Write-Host "Servicio detenido."
    }

    if (Test-Path $PidFile) {
        Remove-Item -Path $PidFile -Force
    }
}

function Main {
    cls
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
