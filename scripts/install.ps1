if (Get-Command py -ErrorAction SilentlyContinue) {
    $PythonCmd = "py"
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $PythonCmd = "python3"
} else {
    Write-Output "Neither 'py' launcher nor 'python3' is available in PATH."
    exit 1
}

& $PythonCmd -m venv "$($env:USERPROFILE)\\.mimic\\.venv"
"$($env:USERPROFILE)\\.mimic\\.venv\\Scripts\\activate"
pip install pipx
pipx install -e "$($env:USERPROFILE)\\.mimic"
pipx ensurepath
Remove-Item "$($env:USERPROFILE)\\.mimic\\.venv" -Recurse -Force -Confirm:$false
