echo "Testing RNP"
rnp_response=$(curl -k -s -o /dev/null -w "%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d '{"question":"Самая высокая рентабельность у заказа"}' \
    https://localhost:8443/adam)

echo $rnp_response

if [ "$rnp_response" -eq 200 ]; then
    echo "✅ RNP bot webhook passed"
else
    echo "❌ RNP bot webhook failed with status $rnp_response"
    exit 1
fi