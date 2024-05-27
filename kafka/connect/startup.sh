# Launch Kafka Connect
/etc/confluent/docker/run &
#
# Wait for Kafka Connect listener
echo "Waiting for Kafka Connect to start listening on localhost ⏳"
while true; do
  curl_status=$(curl -s -o /dev/null -w %{http_code} http://localhost:8083/connectors)
  echo -e $(date) " Kafka Connect listener HTTP state: " $curl_status " (waiting for 200)"
  if [ $curl_status -eq 200 ] ; then
    break
  fi
  sleep 5
done

echo -e "\n--\n+> Creating pre-defined Kafka Connect connectors"
# Check if directory exists
if [ -d "$DEFAULT_CONNECTOR_CONFIGS_DIR" ]; then
  # Loop through all JSON files in the directory
  for file in "$DEFAULT_CONNECTOR_CONFIGS_DIR"/*.json; do
    # Check if file exists
    if [ -f "$file" ]; then
      curl -s -X PUT -H  "Content-Type:application/json" http://localhost:8083/connectors/source-datagen-01/config \
           -d "$(cat "$file")"
    fi
  done
else
  echo "Directory $dir does not exist."
fi

sleep infinity
