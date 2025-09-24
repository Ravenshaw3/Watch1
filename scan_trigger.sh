#!/bin/bash

# Get authentication token
TOKEN=$(curl -s -X POST -H 'Content-Type: application/json' -d '{"username":"admin","password":"admin123"}' http://192.168.254.14:8083/api/v1/auth/login | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

echo "Token: $TOKEN"

# Start media scan
curl -X POST -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' -d '{"directory":"/app/media"}' http://192.168.254.14:8083/api/v1/media/scan

echo "Scan triggered!"

