# CuraPostProcessingScripts

My post processing scripts for Ultimaker Cura. 

[License](LICENSE)

## Install

Run `install.ps1` with admin privileges. 
It will copy the scripts to the appropriate folder inside Cura installation directory.

**Params**

- `CuraVersion` : Specific Cura version to install the script to (ex: `4.10`). If not specified, the highest version installed on the system will be selected.

## Scripts

Overview of the available scripts

Name  | Description
---------|----------
I Like To Move It | Remove all heating and extrusions commands from the gcode. Results in pure and immediate movement. Useful for testing purposes.
You Are Here | Displays job name and current layer on the LCD (with scrolling effect).
