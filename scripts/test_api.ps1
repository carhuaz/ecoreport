param(
    [Parameter(Mandatory=$true)]
    [string]$BaseUrl,

    [string]$Email = "test-ciudadano@ecoreport.pe",
    [string]$Password = "123456"
)

$ErrorActionPreference = "Stop"
$API = $BaseUrl.TrimEnd("/")

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   EcoReport API - Pruebas de humo" -ForegroundColor Cyan
Write-Host "   $BaseUrl" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$passed = 0
$failed = 0

function Test-Endpoint {
    param($Name, $Method, $Path, $Body, $ExpectedStatus = 200, $Headers = @{})

    try {
        $params = @{
            Method = $Method
            Uri = "$API$Path"
            ContentType = "application/json"
            Headers = $Headers
        }
        if ($Body) { $params.Body = ($Body | ConvertTo-Json) }

        $response = Invoke-RestMethod @params
        if ($response.StatusCode -or $LASTEXITCODE) { }
        Write-Host "  ✅ $Name" -ForegroundColor Green
        return $response
    }
    catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        if ($statusCode -eq $ExpectedStatus) {
            Write-Host "  ✅ $Name (esperado $ExpectedStatus)" -ForegroundColor Green
            return $null
        }
        Write-Host "  ❌ $Name - Error: $_" -ForegroundColor Red
        return $null
    }
}

# --- Test 1: Health ---
Write-Host "`n📡 Health Check" -ForegroundColor Yellow
Test-Endpoint -Name "GET /api/health" -Method GET -Path "/api/health"

# --- Test 2: Register ---
Write-Host "`n📝 Registro" -ForegroundColor Yellow
$registerBody = @{
    nombre = "Test Ciudadano"
    email = $Email
    password = $Password
    dni = (Get-Random -Minimum 10000000 -Maximum 99999999).ToString()
}
Test-Endpoint -Name "POST /api/auth/register" -Method POST -Path "/api/auth/register" -Body $registerBody -ExpectedStatus 200

# --- Test 3: Register duplicado (debe fallar si ya existe) ---
Write-Host "`n⚠️  Registro duplicado" -ForegroundColor Yellow
$registerDuplicate = $registerBody.Clone()
$registerDuplicate.dni = (Get-Random -Minimum 10000000 -Maximum 99999999).ToString()
Test-Endpoint -Name "POST /api/auth/register (email repetido)" -Method POST -Path "/api/auth/register" -Body $registerDuplicate -ExpectedStatus 400

# --- Test 4: Login ---
Write-Host "`n🔑 Login" -ForegroundColor Yellow
$loginResponse = Test-Endpoint -Name "POST /api/auth/login" -Method POST -Path "/api/auth/login" -Body @{ email = $Email; password = $Password } -ExpectedStatus 200

$token = $null
if ($loginResponse -and $loginResponse.token) {
    $token = $loginResponse.token
    Write-Host "      Token obtenido: $($token.Substring(0, 30))..." -ForegroundColor Gray
}

# --- Test 5: /api/auth/me ---
Write-Host "`n👤 Obtener perfil" -ForegroundColor Yellow
if ($token) {
    $authHeader = @{ Authorization = "Bearer $token" }
    Test-Endpoint -Name "GET /api/auth/me" -Method GET -Path "/api/auth/me" -Headers $authHeader
}

# --- Test 6: Reportes públicos ---
Write-Host "`n📋 Reportes públicos" -ForegroundColor Yellow
Test-Endpoint -Name "GET /api/reportes/publicos" -Method GET -Path "/api/reportes/publicos"

# --- Test 7: Estadísticas (requiere auth) ---
Write-Host "`n📊 Estadísticas" -ForegroundColor Yellow
if ($token) {
    Test-Endpoint -Name "GET /api/estadisticas/resumen" -Method GET -Path "/api/estadisticas/resumen" -Headers $authHeader
}

# --- Test 8: Mapa ---
Write-Host "`n🗺️  Mapa" -ForegroundColor Yellow
if ($token) {
    Test-Endpoint -Name "GET /api/mapa/reportes" -Method GET -Path "/api/mapa/reportes" -Headers $authHeader
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   Pruebas completadas" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
