#!/bin/bash

if [ "$1" = "api-service" ]; then
  exec gunicorn -b 0.0.0.0:8000 app:app --workers 2
else
  echo "Invalid command, please use one of: api-service"
  exit 1
fi