import requests
import os

# Upload the CSV data to restore functionality
csv_file_path = "modelo_dados_bandit.csv"
upload_url = "http://localhost:8080/upload-data"

if os.path.exists(csv_file_path):
    print(f"📤 Uploading {csv_file_path}...")
    
    with open(csv_file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(upload_url, files=files)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Upload successful!")
        print(f"📊 Processed: {result['processed_rows']} records out of {result['total_rows']} lines")
        if result.get('experiment_ids'):
            print(f"🔢 Updated experiments: {result['experiment_ids']}")
        if result.get('errors'):
            print(f"⚠️ Errors found: {result['total_errors']}")
    else:
        print(f"❌ Upload failed: {response.status_code}")
        print(response.text)
else:
    print(f"❌ File {csv_file_path} not found")

# Test allocation endpoint
print("\n🧮 Testing allocation endpoint...")
allocation_url = "http://localhost:8080/allocation?experiment_id=1&window_days=14"
response = requests.get(allocation_url)

if response.status_code == 200:
    result = response.json()
    print("✅ Allocation endpoint working!")
    print(f"🎯 Allocations: {result.get('allocations', {})}")
    print(f"📈 Algorithm: {result.get('algorithm', 'unknown')}")
else:
    print(f"❌ Allocation failed: {response.status_code}")
    print(response.text)
