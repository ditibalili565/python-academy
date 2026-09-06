#!/bin/zsh

echo
echo "Python Academy - Duke u nisur..."
echo

cd "$(dirname "$0")"

python3 --version >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "GABIM: Python nuk eshte instaluar!"
    read -p "Shtyp Enter..."
    exit
fi

python3 -c "import pygame" >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Duke instaluar pygame..."
    pip3 install pygame
fi

python3 server.py &

sleep 2

open http://localhost:8000/registry.html

echo
echo "Serveri u nis!"