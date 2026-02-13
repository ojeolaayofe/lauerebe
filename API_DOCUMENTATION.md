# E1 Invest Real Estate Platform - Complete API Documentation

## Base URL
`https://real-estate-pro-14.preview.emergentagent.com/api`

## Authentication
All protected endpoints require Bearer token in Authorization header:
```
Authorization: Bearer {token}
```

---

## 1. AUTHENTICATION APIs (`/auth`)

### Send Email OTP
- **POST** `/auth/send-email-otp`
- Body: `{"contact": "email@example.com", "type": "email"}`
- Returns: OTP code for testing

### Verify Email OTP
- **POST** `/auth/verify-email-otp`
- Body: `{"contact": "email@example.com", "code": "123456", "type": "email"}`
- Returns: Access token + user data

### Send WhatsApp OTP
- **POST** `/auth/send-whatsapp-otp`
- Body: `{"contact": "+234XXXXXXXXXX", "type": "whatsapp"}`

### Verify WhatsApp OTP
- **POST** `/auth/verify-whatsapp-otp`
- Body: `{"contact": "+234XXXXXXXXXX", "code": "123456", "type": "whatsapp"}`

### Get Current User
- **GET** `/auth/me` 🔒
- Returns: Current user profile

---

## 2. PROPERTY APIs (`/properties`)

### List Properties
- **GET** `/properties`
- Query params: `property_type`, `location`, `price_min`, `price_max`, `rental_yield_min`, `availability`, `limit`

### Get Property by ID
- **GET** `/properties/{property_id}`

### Create Property (Admin)
- **POST** `/properties` 🔒👑
- Body: Full property object with investment details

### Update Property (Admin)
- **PUT** `/properties/{property_id}` 🔒👑

### Delete Property (Admin)
- **DELETE** `/properties/{property_id}` 🔒👑

---

## 3. AI FEATURES APIs (`/ai`)

### Generate Property Description
- **POST** `/ai/generate-description`
- Body: Property details
- Uses: Gemini 3 Flash

### Get Property Recommendations
- **POST** `/ai/recommendations`
- Body: `{"budget": 5000000, "currency": "NGN", "preferred_location": "Oye Ekiti"}`

### AI Chatbot
- **POST** `/ai/chat`
- Body: `{"message": "What's APY?", "session_id": "unique-session-id"}`

### Investment Projection
- **POST** `/ai/investment-projection`
- Body: `{"property_id": "...", "investment_amount": 5000000, "duration_years": 5}`

---

## 4. INVESTMENT APIs (`/investments`)

### Calculate APY
- **POST** `/investments/calculate-apy`
- Body: `{"principal_amount": 5000000, "apy_rate": 15, "duration_years": 5}`

### Calculate Instalment Plan
- **POST** `/investments/calculate-instalment`
- Body: `{"total_amount": 5000000, "down_payment_percentage": 30, "duration_months": 24, "interest_rate": 0}`

### Create Investment
- **POST** `/investments` 🔒
- Body: Investment details with optional instalment plan

### Get My Investments
- **GET** `/investments/my-investments` 🔒

### Get Investment by ID
- **GET** `/investments/{investment_id}` 🔒

---

## 5. PAYMENT APIs (`/payments`)

### Initialize Payment
- **POST** `/payments/initialize` 🔒
- Body: `{"email": "...", "amount": 5000000, "currency": "NGN", "investment_id": "..."}`
- Returns: Paystack checkout URL

### Verify Payment
- **GET** `/payments/verify/{reference}` 🔒

### Webhook (Paystack callback)
- **POST** `/payments/webhook`

---

## 6. EXIT/RESALE APIs (`/exit-resale`)

### Request Exit
- **POST** `/exit-resale/request-exit` 🔒
- Body: `{"investment_id": "...", "asking_price": 5500000, "reason": "...", "urgent": false}`

### My Exit Requests
- **GET** `/exit-resale/my-exit-requests` 🔒

### Resale Marketplace
- **GET** `/exit-resale/marketplace`
- Returns: All approved exit requests available for purchase

### Purchase Resale Investment
- **POST** `/exit-resale/purchase/{exit_request_id}` 🔒

### Admin: Review Exit Request
- **PUT** `/exit-resale/admin/review/{exit_request_id}` 🔒👑
- Query params: `status=approved/rejected`, `admin_notes`

### Admin: Pending Exit Requests
- **GET** `/exit-resale/admin/pending` 🔒👑

---

## 7. SUPPLIER/LABOUR APIs (`/suppliers`)

### Onboard as Supplier
- **POST** `/suppliers/onboard` 🔒
- Body: Business details, service category, experience, equity interest

### My Supplier Profile
- **GET** `/suppliers/my-profile` 🔒

### My Work Assignments
- **GET** `/suppliers/my-assignments` 🔒

### Update Assignment Status
- **PUT** `/suppliers/update-assignment/{assignment_id}` 🔒
- Body: `{"status": "in_progress/completed", "actual_cost": 150000}`

### Admin: Assign Work
- **POST** `/suppliers/admin/assign-work` 🔒👑
- Body: Work details with equity percentage

### Admin: All Suppliers
- **GET** `/suppliers/admin/all-suppliers` 🔒👑

### Admin: Approve Supplier
- **PUT** `/suppliers/admin/approve-supplier/{supplier_id}` 🔒👑
- Query param: `status=approved/rejected`

---

## 8. REFERRAL PROGRAM APIs (`/referrals`)

### Get My Referral Code
- **GET** `/referrals/my-referral-code` 🔒
- Auto-generates if doesn't exist

### Apply Referral Code
- **POST** `/referrals/apply-referral-code/{code}` 🔒
- User applies someone else's referral code

### My Commissions
- **GET** `/referrals/my-commissions` 🔒
- Returns commission history and total earned

---

## 9. APPOINTMENT BOOKING APIs (`/appointments`)

### Book Property Viewing
- **POST** `/appointments/book` 🔒
- Body: `{"property_id": "...", "appointment_date": "2026-02-15", "appointment_time": "10:00 AM", "visitor_name": "...", "visitor_phone": "...", "visitor_email": "...", "notes": "..."}`

### My Appointments
- **GET** `/appointments/my-appointments` 🔒

### Update Appointment
- **PUT** `/appointments/update/{appointment_id}` 🔒
- Query param: `status=confirmed/cancelled/completed`

---

## 10. DOCUMENT MANAGEMENT APIs (`/documents`)

### Upload Documents
- **POST** `/documents/upload` 🔒
- Query param: `investment_id`
- Form data: Multiple files

### Get Investment Documents
- **GET** `/documents/investment/{investment_id}` 🔒
- Returns list without large file content

### Download Document
- **GET** `/documents/download/{document_id}` 🔒
- Returns base64 content for download

### Delete Document
- **DELETE** `/documents/{document_id}` 🔒

---

## 11. MATERIALS & LABOUR TRACKING APIs (`/materials`)

### Create Materials/Labour Plan
- **POST** `/materials/plan` 🔒👑
- Body: `{"property_id": "...", "materials": [{name, quantity_needed, unit, estimated_cost}], "labour": [{category, workers_needed, days_needed, cost_per_day}]}`

### Get Property Plan
- **GET** `/materials/property/{property_id}`
- Returns plan with progress percentages and remaining amounts

### Contribute to Plan
- **POST** `/materials/contribute/{plan_id}` 🔒
- Body: `{"materials_amount": 50000, "labour_amount": 30000}`

### Get Plan Contributions
- **GET** `/materials/contributions/{plan_id}`

---

## 12. OCCUPANCY TRACKING APIs (`/occupancy`)

### Update Property Occupancy
- **POST** `/occupancy/update` 🔒👑
- Body: `{"property_id": "...", "total_units": 20, "occupied_units": 15, "notes": "..."}`

### Get Property Occupancy
- **GET** `/occupancy/property/{property_id}`
- Returns occupancy rate, available units

### Get All Occupancy Data
- **GET** `/occupancy/all` 🔒👑
- Admin view of all properties

---

## 13. NOTIFICATIONS APIs (`/notifications`)

### My Notifications
- **GET** `/notifications/my-notifications` 🔒
- Returns last 50 notifications

### Mark Notification as Read
- **PUT** `/notifications/mark-read/{notification_id}` 🔒

### Mark All Read
- **PUT** `/notifications/mark-all-read` 🔒

### Unread Count
- **GET** `/notifications/unread-count` 🔒

---

## 14. FILE UPLOAD APIs (`/upload`)

### Upload Images
- **POST** `/upload/images` 🔒👑
- Form data: Multiple image files
- Returns: Base64 data URLs

### Delete Image
- **DELETE** `/upload/images` 🔒👑
- Query param: `image_url`

---

## 15. USER MANAGEMENT APIs (`/users`)

### Get Favorites
- **GET** `/users/favorites` 🔒

### Add to Favorites
- **POST** `/users/favorites/{property_id}` 🔒

### Remove from Favorites
- **DELETE** `/users/favorites/{property_id}` 🔒

### Get Profile
- **GET** `/users/profile` 🔒

### Update Profile
- **PUT** `/users/profile` 🔒
- Body: `{"first_name": "...", "last_name": "...", "phone": "..."}`

---

## 16. ADMIN DASHBOARD APIs (`/admin`)

### Dashboard Statistics
- **GET** `/admin/dashboard-stats` 🔒👑
- Returns: total properties, users, investments, transactions, investment amount

### All Users
- **GET** `/admin/users` 🔒👑

### All Investments
- **GET** `/admin/investments` 🔒👑

### All Transactions
- **GET** `/admin/transactions` 🔒👑

---

## 17. WHATSAPP APIs (`/whatsapp`)

### Send Property Inquiry
- **POST** `/whatsapp/send-inquiry`
- Body: `{"phone_number": "...", "property_id": "...", "message": "..."}`
- Status: MOCKED (no actual WhatsApp sent)

### Book Viewing via WhatsApp
- **POST** `/whatsapp/book-viewing`
- Body: `{"phone_number": "...", "property_id": "...", "viewing_date": "...", "viewing_time": "..."}`
- Status: MOCKED

---

## Legend
- 🔒 = Requires authentication
- 👑 = Requires admin role
- All endpoints return JSON
- Dates in ISO 8601 format
- Currency values in base units (e.g., Naira, not kobo)

## Database Collections
1. users
2. properties
3. investments
4. transactions
5. otp_verifications
6. exit_requests
7. suppliers
8. work_assignments
9. referrals
10. referral_commissions
11. appointments
12. documents
13. materials_labour_plans
14. material_contributions
15. occupancy
16. notifications
17. whatsapp_messages

## Status Codes
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Server Error
