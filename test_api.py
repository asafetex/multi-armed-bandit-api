#!/usr/bin/env python3
import requests
import json

# Test CSV upload
def test_upload():
    print("Testing CSV upload...")
    with open('test_data.csv', 'rb') as f:
        files = {'file': ('test_data.csv', f, 'text/csv')}
        response = requests.post('http://localhost:8081/upload-data', files=files)
        print(f"Upload Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200

# Test allocation calculation
def test_allocation():
    print("\nTesting allocation calculation...")
    response = requests.get('http://localhost:8081/allocation?experiment_id=1')
    print(f"Allocation Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Allocations: {data['allocations']}")
        print(f"Algorithm: {data['algorithm']}")
        print(f"Total impressions: {data['summary']['total_impressions']}")
        return True
    else:
        print(f"Error: {response.text}")
        return False

# Test experiments list
def test_experiments():
    print("\nTesting experiments list...")
    response = requests.get('http://localhost:8081/experiments/')
    print(f"Experiments Status: {response.status_code}")
    if response.status_code == 200:
        experiments = response.json()
        print(f"Found {len(experiments)} experiments")
        for exp in experiments:
            print(f"  - ID {exp['id']}: {exp['name']}")
        return True
    else:
        print(f"Error: {response.text}")
        return False

if __name__ == "__main__":
    print("=== Multi-Armed Bandit API Test ===")
    
    # Test experiments first
    if not test_experiments():
        print("❌ Experiments test failed")
        exit(1)
    
    # Test upload
    if not test_upload():
        print("❌ Upload test failed")
        exit(1)
    
    # Test allocation
    if not test_allocation():
        print("❌ Allocation test failed")
        exit(1)
    
    print("\n✅ All tests passed! System is working correctly.")
