"""
Script to test the Multi-Armed Bandit API
Complete workflow: create experiment -> add data -> get allocation
"""

import requests
import json
from datetime import date, timedelta
import time

BASE_URL = "http://localhost:8000"

def test_api_workflow():
    """Test complete API workflow"""
    
    print("=== Multi-Armed Bandit API Test ===\n")
    
    # 1. Create experiment
    print("1. Creating experiment...")
    experiment_data = {
        "name": "Homepage CTR Optimization",
        "description": "Testing different homepage layouts for better CTR"
    }
    
    response = requests.post(f"{BASE_URL}/experiments", json=experiment_data)
    if response.status_code == 200:
        experiment = response.json()
        experiment_id = experiment["id"]
        print(f"   Created experiment ID: {experiment_id}")
    else:
        print(f"   Error creating experiment: {response.status_code}")
        print(f"   Response: {response.text}")
        return
    
    print()
    
    # 2. Submit historical data (last 10 days)
    print("2. Submitting historical performance data...")
    
    base_date = date.today() - timedelta(days=10)
    
    for day in range(10):
        current_date = base_date + timedelta(days=day)
        
        metric_data = {
            "date": current_date.isoformat(),
            "variants": [
                {
                    "name": "control",
                    "impressions": 1000 + (day * 50),
                    "clicks": int((1000 + (day * 50)) * 0.07),
                    "conversions": 0
                },
                {
                    "name": "variant_a",
                    "impressions": 1000 + (day * 50),
                    "clicks": int((1000 + (day * 50)) * 0.095),
                    "conversions": 0
                },
                {
                    "name": "variant_b", 
                    "impressions": 1000 + (day * 50),
                    "clicks": int((1000 + (day * 50)) * 0.082),
                    "conversions": 0
                }
            ]
        }
        
        response = requests.post(
            f"{BASE_URL}/experiments/{experiment_id}/data",
            json=metric_data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Day {day+1} ({current_date}): {result['total_impressions']} impressions, {result['total_clicks']} clicks")
        else:
            print(f"   Error submitting data for day {day+1}: {response.status_code}")
            print(f"   Response: {response.text}")
    
    print()
    
    # 3. Get optimal allocation
    print("3. Calculating optimal allocation...")
    response = requests.get(f"{BASE_URL}/experiments/{experiment_id}/allocation")
    
    if response.status_code == 200:
        allocation = response.json()
        print(f"   Algorithm: {allocation['algorithm']}")
        print(f"   Target date: {allocation['target_date']}")
        print(f"   Total impressions analyzed: {allocation['total_impressions']}")
        print("   Recommended allocations:")
        
        for variant_alloc in allocation['allocations']:
            print(f"     {variant_alloc['variant']}: {variant_alloc['allocation']:.1%} "
                  f"(CTR: {variant_alloc['ctr']:.3%}, {variant_alloc['clicks']} clicks)")
        
        total_allocation = sum(v['allocation'] for v in allocation['allocations'])
        print(f"   Total allocation: {total_allocation:.3f}")
        
    else:
        print(f"   Error getting allocation: {response.status_code}")
        print(f"   Response: {response.text}")
    
    print()
    
    # 4. Get allocation history
    print("4. Getting allocation history...")
    response = requests.get(f"{BASE_URL}/experiments/{experiment_id}/history")
    
    if response.status_code == 200:
        history = response.json()
        print(f"   Found {len(history['history'])} allocation records")
        
        if history['history']:
            latest = history['history'][0]
            print(f"   Latest allocation ({latest['date']}):")
            for variant, percentage in latest['allocations'].items():
                print(f"     {variant}: {percentage:.1%}")
    
    print("\n=== Test completed ===")

if __name__ == "__main__":
    # Wait for API to be ready
    print("Waiting for API to be ready...")
    for i in range(30):
        try:
            response = requests.get(f"{BASE_URL}/")
            if response.status_code == 200:
                print("API is ready!\n")
                break
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(1)
    else:
        print("API not responding. Make sure it's running on http://localhost:8000")
        exit(1)
    
    # Run tests
    test_api_workflow()