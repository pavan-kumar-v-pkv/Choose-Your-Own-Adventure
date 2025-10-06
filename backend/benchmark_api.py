"""
API Performance Benchmarking Script
Measures response times for resume metrics
"""
import time
import requests
import statistics

BASE_URL = "http://localhost:8000/api"

def benchmark_endpoint(url, method="GET", json_data=None, iterations=5):
    """Benchmark an endpoint multiple times and return stats"""
    times = []
    
    for i in range(iterations):
        start = time.time()
        try:
            if method == "GET":
                response = requests.get(url, timeout=10)
            else:
                response = requests.post(url, json=json_data, timeout=10)
            
            elapsed = (time.time() - start) * 1000  # Convert to milliseconds
            
            if response.status_code in [200, 201]:
                times.append(elapsed)
            else:
                print(f"   ⚠️  Request {i+1} failed with status {response.status_code}")
        except Exception as e:
            print(f"   ❌ Request {i+1} error: {e}")
    
    if not times:
        return None
    
    return {
        "avg": statistics.mean(times),
        "min": min(times),
        "max": max(times),
        "median": statistics.median(times)
    }

print("=" * 60)
print("⚡ API Performance Benchmarking")
print("=" * 60)
print("\nℹ️  Make sure the backend is running on http://localhost:8000")
print("   Start it with: cd backend && uv run python main.py\n")

# Test if server is running
try:
    response = requests.get(f"{BASE_URL}/../docs", timeout=2)
    if response.status_code != 200:
        print("❌ Backend server not responding. Please start it first.")
        exit(1)
except:
    print("❌ Backend server not running. Please start it with:")
    print("   cd backend && uv run python main.py")
    exit(1)

print("✅ Server is running. Starting benchmark...\n")

# Benchmark story retrieval
print("📊 Benchmarking GET /api/stories/{id}/complete")
stats = benchmark_endpoint(f"{BASE_URL}/stories/1/complete", iterations=10)
if stats:
    print(f"   Average: {stats['avg']:.2f}ms")
    print(f"   Median:  {stats['median']:.2f}ms")
    print(f"   Min:     {stats['min']:.2f}ms")
    print(f"   Max:     {stats['max']:.2f}ms")

print("\n" + "=" * 60)
print("✅ Benchmark complete!")
print("=" * 60)
