$workdir = "D:\Coding\Python\Insta-Automate"
$venv = "$workdir\.venv\Scripts\Activate.ps1"
$entrypoint = "$workdir\main.py"

Set-Location -Path $workdir
. $venv
python.exe $entrypoint @args
