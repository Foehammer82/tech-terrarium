#!/bin/bash

echo -e "\n--\n+> Iterating through ingestion config files..."
if [ -d /ingestion_configs ]; then
  for file in /ingestion_configs/*.yaml; do
    if [ -f "$file" ]; then
      datahub ingest -c "$file" || true
    fi
  done
else
  echo "Directory $dir does not exist."
fi

exit 0