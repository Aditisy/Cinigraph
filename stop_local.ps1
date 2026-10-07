$ErrorActionPreference = 'Stop'
$runtimePath = Join-Path $PSScriptRoot '.runtime'
foreach ($serviceName in @('web','llm')) {
    $pidPath = Join-Path $runtimePath ($serviceName + '.pid')
    if (Test-Path $pidPath) {
        $serviceProcessId = [int](Get-Content -LiteralPath $pidPath)
        $serviceProcess = Get-CimInstance Win32_Process -Filter "ProcessId=$serviceProcessId"
        if ($serviceProcess -and $serviceProcess.CommandLine.Contains($PSScriptRoot)) {
            Stop-Process -Id $serviceProcessId
            Write-Output "Stopped $serviceName"
        }
    }
}
# Identify the Java process by this exact private Neo4j home before stopping.
$neoPath = Join-Path $runtimePath 'neo4j-community-2026.09.0'
Get-CimInstance Win32_Process -Filter "Name='java.exe'" | Where-Object {
    $_.CommandLine -and $_.CommandLine.Contains($neoPath)
} | ForEach-Object { Stop-Process -Id $_.ProcessId; Write-Output 'Stopped private Neo4j' }
