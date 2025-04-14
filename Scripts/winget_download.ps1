$id = (Get-Clipboard).Trim()
Write-Output "Package ID: $id"
Write-Output "Fetching download URL, Please wait..."
$details = (winget show $id)
$downloadUri = ($details | Select-String -Pattern "Installer Url: (https?://\S+)" -AllMatches)
# Check valid URI and get URL
if ($null -eq $downloadUri){
    Write-Output "Invalid package"
    exit 1
} else {
    $downloadUrl = $downloadUri.Matches.Groups[1].Value
    $package = Split-Path -Path $downloadUrl -Leaf
    $destination = "$env:USERPROFILE\Desktop\$package"
}
Write-Output $downloadUrl
Write-Output "Started downloading >>> $destination"
Invoke-WebRequest $downloadUrl -OutFile $destination
