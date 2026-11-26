#!/usr/bin/env bash

for i in {1..10}; do
	curl -s -X POST http://localhost:8000/notes -H 'Content-Type: application/json' -d "{\"title\": \"Нотатка: $i\" }" | jq -r '"Створено нотатку id = \(.id)"' 
done;
