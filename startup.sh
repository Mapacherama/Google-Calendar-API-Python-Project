#!/bin/bash
cd /home/site/wwwroot
python3 -m venv /home/site/wwwroot/antenv
source /home/site/wwwroot/antenv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000