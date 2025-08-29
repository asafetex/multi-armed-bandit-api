import requests
import json

# Test allocation endpoint and inspect the response structure
allocation_url = "http://localhost:8080/allocation?experiment_id=1&window_days=14"
response = requests.get(allocation_url)

print(f"Status Code: {response.status_code}")
print(f"Headers: {response.headers}")
print(f"Raw Response:")
print(response.text)
print("\n" + "="*50 + "\n")

if response.status_code == 200:
    try:
        result = response.json()
        print("Parsed JSON:")
        print(json.dumps(result, indent=2))
        
        print("\n" + "="*50 + "\n")
        print("Structure Analysis:")
        print(f"- allocations: {result.get('allocations', 'NOT FOUND')}")
        print(f"- summary: {result.get('summary', 'NOT FOUND')}")
        print(f"- summary.variants: {result.get('summary', {}).get('variants', 'NOT FOUND')}")
        
    except Exception as e:
        print(f"JSON Parse Error: {e}")
else:
    print("Request failed")
