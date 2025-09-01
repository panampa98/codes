$path = "C:\Users\USER\Documents"

# Verificar ruta
if (-Not (Test-Path $path)) {
    Write-Host "❌ Ruta no encontrada: $path"
    exit
}

# Obtener contenido (carpetas + archivos)
$items = Get-ChildItem -LiteralPath $path

$result = @()

foreach ($item in $items) {
    if ($item.PSIsContainer) {
        # Si es carpeta -> sumar tamaño de archivos dentro
        $size = (Get-ChildItem -LiteralPath $item.FullName -Recurse -File -ErrorAction SilentlyContinue |
                 Measure-Object Length -Sum).Sum
    }
    else {
        # Si es archivo -> su tamaño directo
        $size = $item.Length
    }

    $result += [PSCustomObject]@{
        Name  = $item.Name
        SizeMB = "{0:N2}" -f ($size / 1MB)
    }
}

# Ordenar de mayor a menor
$result | Sort-Object {[double]$_.SizeMB} -Descending | Format-Table -AutoSize
