py -m venv "$($env:USERPROFILE)\\.mimic\\.venv"
"$($env:USERPROFILE)\\.mimic\\.venv\\Scripts\\activate"
pip install pipx
pipx uninstall mimic
deactivate
Remove-Item "$($env:USERPROFILE)\\.mimic" -Recurse -Force -Confirm:$false
