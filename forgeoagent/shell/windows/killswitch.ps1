$desktopPath = [System.IO.Path]::Combine($env:USERPROFILE, 'Desktop')
$hiddenFile = [System.IO.Path]::Combine($desktopPath, '.killswitch')

if (-not (Test-Path -Path $hiddenFile)) {
    if (-not (Test-Path -Path $desktopPath)) {
        New-Item -ItemType Directory -Path $desktopPath | Out-Null
    }
    New-Item -ItemType File -Path $hiddenFile | Out-Null
    Write-Output "Hidden file '$hiddenFile' created successfully on your Desktop."
} else {
    Write-Output "Hidden file '$hiddenFile' already exists on your Desktop."
}
