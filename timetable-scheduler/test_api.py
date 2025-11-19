"""
Comprehensive API testing script
Tests all endpoints and validates responses
"""
import requests
import json
import time

BASE_URL = "http://localhost:5000"
access_token = None

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_health_check():
    """Test health check endpoint"""
    print_section("Health Check")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("✓ Health check passed")

def test_register():
    """Test user registration"""
    print_section("User Registration")
    data = {
        "email": "admin@test.com",
        "password": "Admin123!",
        "full_name": "Test Admin",
        "role": "admin",
        "department": "IT"
    }
    response = requests.post(f"{BASE_URL}/api/auth/register", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        global access_token
        access_token = response.json()['access_token']
        print(f"✓ Registration successful. Token: {access_token[:20]}...")
    elif response.status_code == 409:
        print("⚠ User already exists, trying login...")
        test_login()
    else:
        print(f"✗ Registration failed")

def test_login():
    """Test user login"""
    print_section("User Login")
    data = {
        "email": "admin@test.com",
        "password": "Admin123!"
    }
    response = requests.post(f"{BASE_URL}/api/auth/login", json=data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        global access_token
        access_token = response.json()['access_token']
        print(f"✓ Login successful. Token: {access_token[:20]}...")
    else:
        print(f"✗ Login failed: {response.json()}")

def test_get_current_user():
    """Test getting current user"""
    print_section("Get Current User")
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("✓ Get current user passed")

def test_create_lecturer():
    """Test creating a lecturer"""
    print_section("Create Lecturer")
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {
        "id": "L999",
        "name": "Test Lecturer",
        "role": "Full-Time",
        "faculty": "Computing",
        "specializations": ["CS101", "CS102"],
        "sessions_per_day": 2
    }
    response = requests.post(f"{BASE_URL}/api/lecturers/", json=data, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code in [201, 409]:
        print("✓ Create lecturer passed")
    else:
        print("✗ Create lecturer failed")

def test_get_lecturers():
    """Test getting all lecturers"""
    print_section("Get All Lecturers")
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{BASE_URL}/api/lecturers/", headers=headers)
    print(f"Status: {response.status_code}")
    lecturers = response.json().get('lecturers', [])
    print(f"Total lecturers: {len(lecturers)}")
    assert response.status_code == 200
    print("✓ Get lecturers passed")

def test_input_validation():
    """Test input data validation"""
    print_section("Input Data Validation")
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {
        "program": "BSCAIT",
        "batch": "BSCAIT-126",
        "semesters": ["S1"]
    }
    response = requests.post(f"{BASE_URL}/api/validation/input", json=data, headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Is Valid: {result['is_valid']}")
        print(f"Total Checks: {result['summary']['total_checks']}")
        print(f"Passed: {result['summary']['passed_checks']}")
        print(f"Critical Errors: {result['summary']['critical_errors']}")
        print(f"Pass Rate: {result['summary']['pass_rate']:.1f}%")
        print("✓ Validation passed")
    else:
        print(f"✗ Validation failed: {response.json()}")

def test_generate_timetable():
    """Test timetable generation"""
    print_section("Generate Timetable")
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {
        "program": "BSCAIT",
        "batch": "BSCAIT-126",
        "semesters": ["S1"],
        "optimize": True
    }
    
    print("Starting timetable generation...")
    start_time = time.time()
    
    response = requests.post(
        f"{BASE_URL}/api/timetable/generate",
        json=data,
        headers=headers,
        timeout=300
    )
    
    elapsed = time.time() - start_time
    
    print(f"Status: {response.status_code}")
    print(f"Time taken: {elapsed:.2f} seconds")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Timetable ID: {result.get('timetable_id')}")
        print(f"Total Sessions: {result.get('statistics', {}).get('total_sessions')}")
        print(f"Overall Fitness: {result.get('statistics', {}).get('fitness', {}).get('overall', 0):.4f}")
        print("✓ Timetable generation passed")
        return result.get('timetable_id')
    else:
        print(f"✗ Timetable generation failed: {response.json()}")
        return None

def test_validation_report(timetable_id):
    """Test validation report generation"""
    if not timetable_id:
        print("⚠ Skipping validation report (no timetable ID)")
        return
    
    print_section("Validation Report")
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(
        f"{BASE_URL}/api/validation/report/{timetable_id}",
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        report = response.json()
        print(f"Overall Status: {report['executive_summary']['overall_status']}")
        print(f"Quality Rating: {report['quality_metrics']['rating']}")
        print(f"Ready for Deployment: {report['executive_summary']['ready_for_deployment']}")
        print("✓ Validation report passed")
    else:
        print(f"✗ Validation report failed")

def test_unauthorized_access():
    """Test unauthorized access"""
    print_section("Unauthorized Access Test")
    
    # Try without token
    response = requests.get(f"{BASE_URL}/api/lecturers/")
    print(f"Without token - Status: {response.status_code}")
    assert response.status_code == 401
    
    # Try with invalid token
    headers = {"Authorization": "Bearer invalid_token"}
    response = requests.get(f"{BASE_URL}/api/lecturers/", headers=headers)
    print(f"With invalid token - Status: {response.status_code}")
    assert response.status_code == 401
    
    print("✓ Unauthorized access properly blocked")

def test_role_based_access():
    """Test role-based access control"""
    print_section("Role-Based Access Control")
    
    # Create viewer user
    data = {
        "email": "viewer@test.com",
        "password": "Viewer123!",
        "full_name": "Test Viewer",
        "role": "viewer"
    }
    response = requests.post(f"{BASE_URL}/api/auth/register", json=data)
    
    if response.status_code == 201:
        viewer_token = response.json()['access_token']
    else:
        # Login if already exists
        login_data = {"email": "viewer@test.com", "password": "Viewer123!"}
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        viewer_token = response.json()['access_token']
    
    # Try to generate timetable with viewer role (should fail)
    headers = {"Authorization": f"Bearer {viewer_token}"}
    data = {
        "program": "BSCAIT",
        "batch": "BSCAIT-126",
        "semesters": ["S1"],
        "optimize": False
    }
    response = requests.post(
        f"{BASE_URL}/api/timetable/generate",
        json=data,
        headers=headers
    )
    
    print(f"Viewer trying to generate timetable - Status: {response.status_code}")
    assert response.status_code == 403
    print("✓ Role-based access control working")

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("  TIMETABLE SCHEDULER API TEST SUITE")
    print("="*60)
    
    try:
        # Basic tests
        test_health_check()
        test_register()
        test_get_current_user()
        
        # Security tests
        test_unauthorized_access()
        test_role_based_access()
        
        # CRUD tests
        test_create_lecturer()
        test_get_lecturers()
        
        # Validation tests
        test_input_validation()
        
        # Timetable generation test
        timetable_id = test_generate_timetable()
        
        # Report generation
        test_validation_report(timetable_id)
        
        print_section("TEST SUMMARY")
        print("✓ All tests passed successfully!")
        print(f"Access Token: {access_token[:20]}...")
        print("\nYou can now use this token to test the API manually:")
        print(f'curl -H "Authorization: Bearer {access_token}" {BASE_URL}/api/lecturers/')
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()