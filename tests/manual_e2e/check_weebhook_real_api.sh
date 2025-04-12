#!/bin/bash

# Test 1: Health check endpoint
echo "Testing health check endpoint..."
response=$(curl -k -s -o /dev/null -w "%{http_code}" https://localhost:8443/)
if [ "$response" -eq 200 ]; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed with status $response"
    exit 1
fi

# Test 2: Manager bot webhook with /start command
echo "Testing manager bot webhook with /start command..."
manager_response=$(curl -k -s -o /dev/null -w "%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d @start_message.json \
    https://localhost:8443/webhook/manager)

if [ "$manager_response" -eq 200 ]; then
    echo "✅ Manager bot webhook passed"
else
    echo "❌ Manager bot webhook failed with status $manager_response"
    exit 1
fi
#
# Test 3: Example bot webhook with text message
echo "Testing example bot webhook with text message..."
example_response=$(curl -k -s -o /dev/null -w "%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d @start_message.json \
    https://localhost:8443/webhook/example)

if [ "$example_response" -eq 200 ]; then
    echo "✅ Example bot webhook passed"
else
    echo "❌ Example bot webhook failed with status $example_response"
    exit 1
fi

echo "All webhook tests completed successfully!"
