# Author : Emanuele Messina
# Description : Installer for the cura post processing scripts.

param (
    [string]$CuraVersion
)

##################################################################################

function Write-Red {
    param (
        [string]$Message
    )
    Write-Host $Message -ForegroundColor Red
}

function IsAdmin {
    $currentIdentity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $currentPrincipal = New-Object Security.Principal.WindowsPrincipal($currentIdentity)
    return $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function CopyPythonScripts {

    param (
        [string]$DestinationFolder
    )

    $scriptsPath = Join-Path $PSScriptRoot "scripts"
    $pythonFiles = Get-ChildItem $scriptsPath -Filter "*.py" -File

    if ($pythonFiles.Count -eq 0) {
        Write-Host "No .py files found in the 'scripts' folder."
        exit
    }

    Write-Host "Copying scripts from $scriptsPath to $DestinationFolder..."

    foreach ($file in $pythonFiles) {

        try {
            Copy-Item $file.FullName -Destination $DestinationFolder -ErrorAction Stop
        }
        catch {
            Write-Red "Error: $_"
            exit
        }

        Write-Host "Copied $($file.Name)"
    }
}

function GetCuraInstallationPath {
    param (
        [string]$SpecificVersion
    )

    $curaEntries = Get-ChildItem "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        "HKLM:\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall", 
        "HKCU:\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall" -ErrorAction SilentlyContinue |
        Get-ItemProperty |
        Where-Object { $_.DisplayName -like "Ultimaker Cura*" } |
        Select-Object DisplayName, UninstallString

    if ($curaEntries.Count -eq 0) {
        Write-Red "Cura is not installed on this machine."
        exit
    }

    if (-Not [string]::IsNullOrWhiteSpace($SpecificVersion)) {
        Write-Host "Requested Cura version $SpecificVersion"
        $specificVersionEntry = $curaEntries | Where-Object { $_.DisplayName -match "Ultimaker Cura $SpecificVersion" }
        if ($specificVersionEntry) {
            $installPath = $specificVersionEntry.UninstallString -replace "(.*\\)(.*unins.*?$)", '$1'
            Write-Host "Found at $installPath"
            return $installPath.TrimEnd('\')
        }
        else {
            Write-Red "Cura version '$SpecificVersion' is not found."
            exit
        }
    }

    Write-Host "Searching for highest Cura version..."

    $sortedCuraEntries = $curaEntries | Sort-Object { [Version]($_.DisplayName -replace "Ultimaker Cura ") } -Descending
    $highestVersionEntry = $sortedCuraEntries[0]

    $installPath = $highestVersionEntry.UninstallString -replace "(.*\\)(.*unins.*?$)", '$1'

    Write-Host "Found highest at $installPath"

    return $installPath.TrimEnd('\')
}

##################################################################################

# Check if the script is running with admin privileges
if (-Not (IsAdmin)) {
    Write-Red "Run this script with admin privileges"
    Pause
    exit
}

# Main script execution

$DestinationFolder = GetCuraInstallationPath -SpecificVersion $CuraVersion
$DestinationFolder = Join-Path $DestinationFolder "share\cura\plugins\PostProcessingPlugin\scripts"

if ( (Test-Path $DestinationFolder) ) {
    CopyPythonScripts -DestinationFolder $DestinationFolder
} else {
    Write-Red "The specified destination folder does not exist."
}

##################################################################################

Pause