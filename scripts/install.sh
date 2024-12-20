python3 -m venv ~/.mimic/.venv
source ~/.mimic/.venv/bin/activate
pip install pipx
pipx install -e ~/.mimic
pipx ensurepath
deactivate
rm -rf ~/.mimic/.venv
