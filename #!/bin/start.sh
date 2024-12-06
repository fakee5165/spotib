#!/bin/bash
gunicorn main:main --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
