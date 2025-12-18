"""
Diagnostic script to test API endpoint performance and identify bottlenecks
"""
import requests
import time
import sys

BASE_URL = "http://localhost:8000"

def test_endpoint(name, url, headers=None, timeout=30):
    """Test a single endpoint and measure performance"""
    print(f"\n{'='*70}")
    print(f"Testing: {name}")
    print(f"URL: {url}")
    print(f"{'='*70}")
    
    try:
        start_time = time.time()
        print(f"⏱️  Starting request at {time.strftime('%H:%M:%S')}")
        
        response = requests.get(url, headers=headers, timeout=timeout)
        
        elapsed = time.time() - start_time
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"⏱️  Response Time: {elapsed:.3f} seconds")
        print(f"📦 Response Size: {len(response.content):,} bytes ({len(response.content)/1024:.1f} KB)")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, dict):
                    print(f"📊 Response Keys: {list(data.keys())}")
                    
                    # For electives, show some stats
                    if 'elective_groups' in data:
                        groups = data['elective_groups']
                        total_options = sum(len(g.get('options', [])) for g in groups.values())
                        print(f"📚 Elective Groups: {len(groups)}")
                        print(f"📚 Total Elective Options: {total_options}")
                    
                    # For progress, show stats
                    if 'completed_credits' in data:
                        print(f"🎓 Progress: {data.get('percent_complete', 0):.1f}%")
                        print(f"📖 Core Remaining: {len(data.get('core_remaining', []))}")
                        print(f"📖 Discipline Electives Remaining: {len(data.get('discipline_elective_placeholders_remaining', []))}")
                
            except Exception as e:
                print(f"⚠️  Could not parse JSON: {e}")
        else:
            print(f"❌ Error: {response.text[:200]}")
            
        return elapsed
        
    except requests.Timeout:
        print(f"❌ REQUEST TIMED OUT after {timeout} seconds")
        return None
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return None


def main():
    print("="*70)
    print("API Performance Diagnostic Tool")
    print("="*70)
    print("Testing backend endpoints to identify bottlenecks...")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend server is running")
        else:
            print(f"⚠️  Backend returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot connect to backend at {BASE_URL}")
        print(f"   Error: {e}")
        print("\n💡 Make sure the backend is running: cd backend && python run.py")
        sys.exit(1)
    
    # Get test token (you'll need to login first or use a valid token)
    print("\n💡 Note: Some endpoints require authentication.")
    print("   Testing public endpoints first...\n")
    
    results = {}
    
    # Test 1: List variants (should be fast - cached)
    results['variants'] = test_endpoint(
        "List Variants",
        f"{BASE_URL}/api/catalogue/variants"
    )
    
    # Test 2: Get electives (this might be slow)
    results['electives'] = test_endpoint(
        "Get Electives for 202301-normal",
        f"{BASE_URL}/api/catalogue/variant/202301-normal/electives"
    )
    
    # Test 3: Get all courses (for comparison)
    results['courses'] = test_endpoint(
        "Get All Courses for 202301-normal",
        f"{BASE_URL}/api/catalogue/variant/202301-normal/courses"
    )
    
    # If you have a valid token, test authenticated endpoints
    token = input("\n🔑 Enter your auth token (or press Enter to skip authenticated tests): ").strip()
    
    if token:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test 4: Student progress
        results['student_progress'] = test_endpoint(
            "Get Student Progress",
            f"{BASE_URL}/api/catalogue/student/progress?intake=202301&entry_type=normal",
            headers=headers
        )
        
        # Test 5: Student stats
        results['student_stats'] = test_endpoint(
            "Get Student Stats",
            f"{BASE_URL}/api/students/stats",
            headers=headers
        )
    
    # Summary
    print("\n" + "="*70)
    print("PERFORMANCE SUMMARY")
    print("="*70)
    
    for name, elapsed in results.items():
        if elapsed is not None:
            status = "🟢 FAST" if elapsed < 1.0 else "🟡 SLOW" if elapsed < 5.0 else "🔴 VERY SLOW"
            print(f"{status} {name:20s}: {elapsed:.3f}s")
        else:
            print(f"❌ {name:20s}: FAILED/TIMEOUT")
    
    # Recommendations
    print("\n" + "="*70)
    print("RECOMMENDATIONS")
    print("="*70)
    
    slow_endpoints = [name for name, elapsed in results.items() if elapsed and elapsed > 2.0]
    
    if slow_endpoints:
        print("⚠️  Slow endpoints detected:")
        for endpoint in slow_endpoints:
            print(f"   - {endpoint}")
        
        print("\n💡 Possible solutions:")
        print("   1. Check network connection between frontend and backend")
        print("   2. Verify Cassandra database is responding quickly")
        print("   3. Check backend logs for errors or warnings")
        print("   4. Consider adding more caching for large responses")
        print("   5. Reduce payload size by limiting elective options")
    else:
        print("✅ All endpoints are performing well!")
    
    print("\n💡 To check browser performance:")
    print("   1. Open browser DevTools (F12)")
    print("   2. Go to Network tab")
    print("   3. Click Academic Planner tab")
    print("   4. Look for slow requests or large payloads")
    print("   5. Check Console tab for JavaScript errors")


if __name__ == '__main__':
    main()
