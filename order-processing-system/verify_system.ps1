# Script de Verificacion del Sistema de Procesamiento de Ordenes
Write-Host "`nINICIANDO VERIFICACION COMPLETA DEL SISTEMA" -ForegroundColor Cyan
Write-Host "======================================================================`n" -ForegroundColor Cyan

$results = @{}

# TEST 1: Health Checks
Write-Host "`n======================================================================" -ForegroundColor Cyan
Write-Host "  TEST 1: HEALTH CHECKS DE SERVICIOS" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

$services = @('8001', '8002', '8003', '8004')
$serviceNames = @('Order', 'Inventory', 'Payment', 'Notification')
$allHealthy = $true

for ($i = 0; $i -lt $services.Count; $i++) {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:$($services[$i])/health" -Method Get -TimeoutSec 5
        Write-Host "[OK] $($serviceNames[$i]) Service (Port $($services[$i]))" -ForegroundColor Green
    }
    catch {
        Write-Host "[FAIL] $($serviceNames[$i]) Service (Port $($services[$i]))" -ForegroundColor Red
        $allHealthy = $false
    }
}

$results['health_checks'] = $allHealthy

# TEST 2: Crear Orden
Write-Host "`n======================================================================" -ForegroundColor Cyan
Write-Host "  TEST 2: CREAR ORDEN" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

$customerId = [guid]::NewGuid().ToString()
$productId = [guid]::NewGuid().ToString()

Write-Host "[INFO] Customer ID: $customerId" -ForegroundColor Yellow
Write-Host "[INFO] Product ID: $productId" -ForegroundColor Yellow

$body = @"
{
  "customer_id": "$customerId",
  "items": [
    {
      "product_id": "$productId",
      "quantity": 2,
      "price": 29.99
    }
  ]
}
"@

try {
    $order = Invoke-RestMethod -Uri "http://localhost:8001/orders/" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 10
    Write-Host "[OK] Orden creada exitosamente!" -ForegroundColor Green
    Write-Host "     Order ID: $($order.id)" -ForegroundColor White
    Write-Host "     Status: $($order.status)" -ForegroundColor White
    Write-Host "     Total: `$$($order.total_amount)" -ForegroundColor White
    $orderId = $order.id
    $results['create_order'] = $true
}
catch {
    Write-Host "[FAIL] Error al crear orden" -ForegroundColor Red
    Write-Host "       $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        Write-Host "       Detalles: $($_.ErrorDetails.Message)" -ForegroundColor Red
    }
    $results['create_order'] = $false
    $orderId = $null
}

# TEST 3: Obtener Orden
if ($orderId) {
    Write-Host "`n======================================================================" -ForegroundColor Cyan
    Write-Host "  TEST 3: CONSULTAR ORDEN POR ID" -ForegroundColor Cyan
    Write-Host "======================================================================" -ForegroundColor Cyan
    
    try {
        $orderResponse = Invoke-RestMethod -Uri "http://localhost:8001/orders/$orderId" -Method Get -TimeoutSec 5
        Write-Host "[OK] Orden consultada exitosamente!" -ForegroundColor Green
        Write-Host "     Status: $($orderResponse.status)" -ForegroundColor White
        $results['get_order'] = $true
    }
    catch {
        Write-Host "[FAIL] Error al consultar orden" -ForegroundColor Red
        $results['get_order'] = $false
    }
    
    # TEST 4: Listar Ordenes del Cliente
    Write-Host "`n======================================================================" -ForegroundColor Cyan
    Write-Host "  TEST 4: LISTAR ORDENES DE CLIENTE" -ForegroundColor Cyan
    Write-Host "======================================================================" -ForegroundColor Cyan
    
    try {
        $customerOrders = Invoke-RestMethod -Uri "http://localhost:8001/orders/customer/$customerId" -Method Get -TimeoutSec 5
        Write-Host "[OK] Ordenes listadas exitosamente!" -ForegroundColor Green
        Write-Host "     Total de ordenes: $($customerOrders.Count)" -ForegroundColor White
        $results['list_orders'] = $true
    }
    catch {
        Write-Host "[FAIL] Error al listar ordenes" -ForegroundColor Red
        $results['list_orders'] = $false
    }
    
    # TEST 5: Procesamiento de Eventos
    Write-Host "`n======================================================================" -ForegroundColor Cyan
    Write-Host "  TEST 5: PROCESAMIENTO DE EVENTOS" -ForegroundColor Cyan
    Write-Host "======================================================================" -ForegroundColor Cyan
    
    Write-Host "[INFO] Esperando 5 segundos para procesamiento de eventos..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    
    try {
        $finalOrder = Invoke-RestMethod -Uri "http://localhost:8001/orders/$orderId" -Method Get -TimeoutSec 5
        Write-Host "[OK] Estado verificado!" -ForegroundColor Green
        Write-Host "     Estado de la orden: $($finalOrder.status)" -ForegroundColor White
        $results['event_processing'] = $true
    }
    catch {
        Write-Host "[FAIL] Error al verificar eventos" -ForegroundColor Red
        $results['event_processing'] = $false
    }
}

# RESUMEN
Write-Host "`n======================================================================" -ForegroundColor Cyan
Write-Host "  RESUMEN DE VERIFICACION" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

$passed = 0
$total = $results.Count

foreach ($key in $results.Keys) {
    $testName = $key -replace '_', ' '
    if ($results[$key]) {
        Write-Host "[PASS] $testName" -ForegroundColor Green
        $passed++
    }
    else {
        Write-Host "[FAIL] $testName" -ForegroundColor Red
    }
}

Write-Host "`n======================================================================" -ForegroundColor Cyan
Write-Host "RESULTADO FINAL: $passed/$total tests pasaron" -ForegroundColor Cyan
Write-Host "======================================================================`n" -ForegroundColor Cyan

if ($passed -eq $total) {
    Write-Host "TODOS LOS TESTS PASARON!" -ForegroundColor Green
    exit 0
}
else {
    Write-Host "Algunos tests fallaron" -ForegroundColor Yellow
    exit 1
}
