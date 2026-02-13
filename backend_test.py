import requests
import sys
import json
from datetime import datetime

class RealEstateAPITester:
    def __init__(self, base_url="https://real-estate-pro-14.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_user_email = f"test_user_{datetime.now().strftime('%H%M%S')}@example.com"
        self.test_otp_code = None

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}
        
        if self.token and 'Authorization' not in headers:
            headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=data)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(str(response_data)) < 200:
                        print(f"   Response: {response_data}")
                except:
                    pass
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text[:200]}")

            return success, response.json() if response.content else {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test API root endpoint"""
        success, response = self.run_test(
            "API Root",
            "GET",
            "",
            200
        )
        return success

    def test_properties_list(self):
        """Test properties list endpoint"""
        success, response = self.run_test(
            "Properties List",
            "GET", 
            "properties",
            200
        )
        if success and isinstance(response, list):
            print(f"   Found {len(response)} properties")
        return success

    def test_properties_with_filters(self):
        """Test properties with filters"""
        success, response = self.run_test(
            "Properties with Filters",
            "GET",
            "properties",
            200,
            data={"limit": 10, "availability": "available"}
        )
        return success

    def test_send_email_otp(self):
        """Test sending email OTP"""
        success, response = self.run_test(
            "Send Email OTP",
            "POST",
            "auth/send-email-otp",
            200,
            data={"contact": self.test_user_email, "type": "email"}
        )
        
        if success and response.get("otp_for_testing"):
            self.test_otp_code = response["otp_for_testing"]
            print(f"   OTP Code: {self.test_otp_code}")
        
        return success

    def test_verify_email_otp(self):
        """Test verifying email OTP"""
        if not self.test_otp_code:
            print("❌ Skipped - No OTP code available")
            return False
            
        success, response = self.run_test(
            "Verify Email OTP",
            "POST",
            "auth/verify-email-otp",
            200,
            data={
                "contact": self.test_user_email,
                "code": self.test_otp_code,
                "type": "email"
            }
        )
        
        if success and response.get("access_token"):
            self.token = response["access_token"]
            print(f"   Token received")
        
        return success

    def test_calculate_apy(self):
        """Test APY calculation"""
        success, response = self.run_test(
            "Calculate APY",
            "POST",
            "investments/calculate-apy",
            200,
            data={
                "principal_amount": 1000000,
                "apy_rate": 15.0,
                "duration_years": 5
            }
        )
        
        if success:
            print(f"   Total Returns: {response.get('total_returns')}")
            print(f"   Monthly Income: {response.get('monthly_passive_income')}")
        
        return success

    def test_calculate_instalment(self):
        """Test instalment calculation"""
        success, response = self.run_test(
            "Calculate Instalment",
            "POST",
            "investments/calculate-instalment",
            200,
            data={
                "total_amount": 5000000,
                "down_payment_percentage": 30,
                "duration_months": 24,
                "interest_rate": 12.0
            }
        )
        
        if success:
            print(f"   Down Payment: {response.get('down_payment')}")
            print(f"   Monthly Payment: {response.get('monthly_payment')}")
        
        return success

    def test_property_detail(self):
        """Test property detail endpoint (requires property to exist)"""
        # First get list of properties to find one to test
        success, properties = self.run_test(
            "Get Properties for Detail Test",
            "GET",
            "properties",
            200,
            data={"limit": 1}
        )
        
        if not success or not properties:
            print("   No properties available to test detail endpoint")
            return True  # Consider this passed since no properties exist
            
        property_id = properties[0]['id']
        success, response = self.run_test(
            "Property Detail",
            "GET",
            f"properties/{property_id}",
            200
        )
        
        return success

    def test_user_current_info(self):
        """Test getting current user info (requires auth)"""
        if not self.token:
            print("   Skipped - No authentication token")
            return True
            
        success, response = self.run_test(
            "Get Current User Info",
            "GET",
            "auth/me",
            200
        )
        
        return success

    def test_social_feed(self):
        """Test social media feed"""
        if not self.token:
            print("   Skipped - No authentication token")
            return True
            
        success, response = self.run_test(
            "Social Feed",
            "GET",
            "social/feed",
            200
        )
        
        return success

    def test_materials_property_plan(self):
        """Test materials and labour plan for a property"""
        # Get first property to test
        success, properties = self.run_test(
            "Get Properties for Materials Test",
            "GET",
            "properties",
            200,
            data={"limit": 1}
        )
        
        if not success or not properties:
            print("   No properties available to test materials endpoint")
            return True
            
        property_id = properties[0]['id']
        success, response = self.run_test(
            "Materials Property Plan",
            "GET",
            f"materials/property/{property_id}",
            200
        )
        
        return success

    def test_occupancy_data(self):
        """Test occupancy data for a property"""
        # Get first property to test
        success, properties = self.run_test(
            "Get Properties for Occupancy Test",
            "GET",
            "properties",
            200,
            data={"limit": 1}
        )
        
        if not success or not properties:
            print("   No properties available to test occupancy endpoint")
            return True
            
        property_id = properties[0]['id']
        success, response = self.run_test(
            "Property Occupancy Data",
            "GET",
            f"occupancy/property/{property_id}",
            200
        )
        
        return success

    def test_exit_marketplace(self):
        """Test exit/resale marketplace"""
        success, response = self.run_test(
            "Exit Marketplace",
            "GET",
            "exit-resale/marketplace",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} resale opportunities")
        
        return success

    def test_referral_code(self):
        """Test referral code system"""
        if not self.token:
            print("   Skipped - No authentication token")
            return True
            
        success, response = self.run_test(
            "My Referral Code",
            "GET",
            "referrals/my-referral-code",
            200
        )
        
        if success and response.get("code"):
            print(f"   Referral Code: {response['code']}")
        
        return success

    def test_appointments_list(self):
        """Test appointments list"""
        if not self.token:
            print("   Skipped - No authentication token")
            return True
            
        success, response = self.run_test(
            "My Appointments",
            "GET",
            "appointments/my-appointments",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} appointments")
        
        return success

    def test_notifications_system(self):
        """Test notifications system"""
        if not self.token:
            print("   Skipped - No authentication token")
            return True
            
        # Test unread count
        success, response = self.run_test(
            "Notifications Unread Count",
            "GET",
            "notifications/unread-count",
            200
        )
        
        if success:
            print(f"   Unread Notifications: {response.get('unread_count', 0)}")
        
        # Test notifications list
        success2, response2 = self.run_test(
            "My Notifications",
            "GET",
            "notifications/my-notifications",
            200
        )
        
        if success2 and isinstance(response2, list):
            print(f"   Total Notifications: {len(response2)}")
        
        return success and success2

    def test_investment_report_pdf(self):
        """Test PDF report generation for investments"""
        if not self.token:
            print("   Skipped - No authentication token")
            return True
            
        # Get user's investments first
        success, investments = self.run_test(
            "Get My Investments for PDF Test",
            "GET",
            "investments/my-investments",
            200
        )
        
        if not success or not investments:
            print("   No investments available to test PDF report")
            return True
            
        investment_id = investments[0]['id']
        
        # Test PDF generation (expect PDF binary response)
        url = f"{self.base_url}/reports/investment/{investment_id}"
        headers = {'Authorization': f'Bearer {self.token}'}
        
        try:
            response = requests.get(url, headers=headers)
            success = response.status_code == 200 and response.headers.get('content-type') == 'application/pdf'
            
            self.tests_run += 1
            if success:
                self.tests_passed += 1
                print(f"\n🔍 Testing Investment PDF Report...")
                print(f"✅ Passed - PDF generated successfully ({len(response.content)} bytes)")
            else:
                print(f"\n🔍 Testing Investment PDF Report...")
                print(f"❌ Failed - Status: {response.status_code}, Content-Type: {response.headers.get('content-type')}")
            
            return success
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False

    def test_ai_recommendations(self):
        """Test AI property recommendations"""
        success, response = self.run_test(
            "AI Property Recommendations",
            "POST",
            "ai/recommendations",
            200,
            data={
                "budget": 5000000,
                "currency": "NGN",
                "preferred_location": "Oye Ekiti"
            }
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} AI recommendations")
        
        return success

    def test_dashboard_stats(self):
        """Test admin dashboard statistics (try with current token)"""
        if not self.token:
            print("   Skipped - No authentication token")
            return True
            
        success, response = self.run_test(
            "Dashboard Statistics",
            "GET",
            "admin/dashboard-stats",
            200
        )
        
        # This might fail with 403 if user is not admin, which is expected
        if not success:
            print("   Note: This may fail if user is not admin (expected)")
        
        return success  # We'll consider this test passed even if 403

def main():
    print("🚀 Starting Real Estate Platform API Tests")
    print("=" * 50)
    
    tester = RealEstateAPITester()
    
    # Test core endpoints
    tests = [
        tester.test_root_endpoint,
        tester.test_properties_list,
        tester.test_properties_with_filters,
        tester.test_property_detail,
        tester.test_calculate_apy,
        tester.test_calculate_instalment,
        tester.test_send_email_otp,
        tester.test_verify_email_otp,
        tester.test_user_current_info
    ]
    
    # Run all tests
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with error: {str(e)}")
            tester.tests_run += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    print(f"🎯 Success Rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if tester.tests_passed < tester.tests_run:
        print(f"❌ {tester.tests_run - tester.tests_passed} tests failed")
        return 1
    else:
        print("✅ All tests passed!")
        return 0

if __name__ == "__main__":
    sys.exit(main())