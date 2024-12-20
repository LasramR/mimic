py -m venv "$($env:USERPROFILE)\\.mimic\\.venv"
"$($env:USERPROFILE)\\.mimic\\.venv\\Scripts\\activate"
pip install pipx
pipx install -e "$($env:USERPROFILE)\\.mimic"
pipx ensurepath
deactivate
Remove-Item "$($env:USERPROFILE)\\.mimic\\.venv" -Recurse -Force -Confirm:$false
