#!/usr/bin/env bash

counter=$(curl -s http://localhost:8000/notes | jq 'length')

while [ "$counter" -gt 0 ]; do
	id=$(curl -s -X GET http://localhost:8000/notes | jq -r ' .[0].id ')
	curl -s -X DELETE http://localhost:8000/notes/"$id"
	counter=$((counter - 1))
done;

