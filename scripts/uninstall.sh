python3 -m venv ~/.mimic/.venv
source ~/.mimic/.venv/bin/activate
pip install pipx
pipx uninstall mimic
deactivate
rm -rf ~/.mimic