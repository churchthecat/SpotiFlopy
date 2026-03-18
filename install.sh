#!/bin/bash

echo "Installing SpotiFlopy..."

python3 -m venv myenv
source myenv/bin/activate

pip install -r requirements.txt

echo ""
echo "Installation complete."
echo "Run with:"
echo "./spotiflopy sync"
