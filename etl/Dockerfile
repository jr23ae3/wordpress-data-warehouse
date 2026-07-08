from python:3.11-slim

workdir /workspace

copy etl/requirements.txt /tmp/requirements.txt
run pip install --no-cache-dir -r /tmp/requirements.txt

copy etl /workspace/etl

entrypoint ["python", "etl/load_wordpress_data.py"]
