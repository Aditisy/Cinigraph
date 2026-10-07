$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$runtimePath = Join-Path $PSScriptRoot '.runtime'
$ErrorActionPreference = 'Continue'
$javaInfo = & java -XshowSettings:properties -version 2>&1
$ErrorActionPreference = 'Stop'
$javaHomeLine = $javaInfo | Where-Object { $_.ToString() -match '^\s*java.home\s*=' } | Select-Object -First 1
if ($javaHomeLine) { $env:JAVA_HOME = ($javaHomeLine.ToString() -split '=',2)[1].Trim() }
$neoPath = Join-Path $runtimePath 'neo4j-community-2026.09.0'
$logPath = Join-Path $PSScriptRoot 'logs'
New-Item -ItemType Directory -Force $logPath | Out-Null
$pythonPath = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path $pythonPath)) {
    $pythonPath = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
}
if (-not (Test-Path $pythonPath)) { $pythonPath = (Get-Command python).Source }
$env:PYTHONPATH = Join-Path $runtimePath 'python'
if (-not (Test-Path (Join-Path $PSScriptRoot 'config.json'))) {
    Copy-Item (Join-Path $PSScriptRoot 'config.local.example.json') (Join-Path $PSScriptRoot 'config.json')
}
$passwordPath = Join-Path $runtimePath 'password.txt'
if (-not (Test-Path $passwordPath)) {
    $localPassword = [Guid]::NewGuid().ToString('N')
    [System.IO.File]::WriteAllText($passwordPath, $localPassword)
}
$env:NEO4J_PASSWORD = [System.IO.File]::ReadAllText($passwordPath).Trim()
if (-not (Test-Path (Join-Path $runtimePath 'auth-initialized'))) {
    & (Join-Path $neoPath 'bin\neo4j-admin.bat') dbms set-initial-password $env:NEO4J_PASSWORD | Out-Null
    if ($LASTEXITCODE -ne 0) { throw 'Neo4j initialization failed.' }
    'initialized' | Set-Content (Join-Path $runtimePath 'auth-initialized')
}
$confPath = Join-Path $neoPath 'conf\neo4j.conf'
@'
server.default_listen_address=127.0.0.1
server.bolt.listen_address=:7689
server.http.listen_address=:7479
server.https.enabled=false
server.memory.heap.initial_size=256m
server.memory.heap.max_size=512m
server.memory.pagecache.size=256m
dbms.usage_report.enabled=false
'@ | Set-Content -LiteralPath $confPath
if (-not (Test-NetConnection -ComputerName 127.0.0.1 -Port 7689 -InformationLevel Quiet -WarningAction SilentlyContinue)) {
    $neoScript = Join-Path $neoPath 'bin\neo4j.ps1'
    $neoProc = Start-Process powershell.exe -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-File',('"' + $neoScript + '"'),'console') -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $logPath 'neo4j.out.log') -RedirectStandardError (Join-Path $logPath 'neo4j.err.log')
    $neoProc.Id | Set-Content (Join-Path $runtimePath 'neo4j.pid')
}
try { $null = Invoke-WebRequest 'http://127.0.0.1:8081/health' -TimeoutSec 2; $llmReady = $true } catch { $llmReady = $false }
if (-not $llmReady) {
    $llmProc = Start-Process (Join-Path $runtimePath 'llama\llama-server.exe') -ArgumentList @('-m',('"' + (Join-Path $runtimePath 'model-3b.gguf') + '"'),'--host','127.0.0.1','--port','8081','-c','4096','-t','4','--parallel','1') -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $logPath 'llm.out.log') -RedirectStandardError (Join-Path $logPath 'llm.err.log')
    $llmProc.Id | Set-Content (Join-Path $runtimePath 'llm.pid')
}
& $pythonPath (Join-Path $PSScriptRoot 'initialize_graph.py')
if ($LASTEXITCODE -ne 0) { throw 'Graph initialization failed. Check logs.' }
try { $null = Invoke-WebRequest 'http://127.0.0.1:8765/api/status' -TimeoutSec 2; $webReady = $true } catch { $webReady = $false }
if (-not $webReady) {
    $webProc = Start-Process $pythonPath -ArgumentList ('"' + (Join-Path $PSScriptRoot 'web_app.py') + '"') -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $logPath 'web.out.log') -RedirectStandardError (Join-Path $logPath 'web.err.log')
    $webProc.Id | Set-Content (Join-Path $runtimePath 'web.pid')
}
for ($readyAttempt = 0; $readyAttempt -lt 20; $readyAttempt++) {
    try { $null = Invoke-WebRequest 'http://127.0.0.1:8765/api/status' -TimeoutSec 2; break } catch { Start-Sleep -Milliseconds 500 }
}
Write-Output 'CineGraph: http://127.0.0.1:8765'
