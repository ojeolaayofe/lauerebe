from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    BUYER = "buyer"
    SELLER = "seller"
    INVESTOR = "investor"
    SUPPLIER = "supplier"
    ADMIN = "admin"
    DIASPORA = "diaspora"

class PropertyType(str, Enum):
    APARTMENT = "apartment"
    HOSTEL = "hostel"
    INVESTMENT_UNIT = "investment_unit"
    ESTATE_BLOCK = "estate_block"

class InvestmentStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Currency(str, Enum):
    NGN = "NGN"
    USD = "USD"
    GBP = "GBP"

# User Models
class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    email: EmailStr
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: UserRole = UserRole.BUYER
    email_verified: bool = False
    whatsapp_verified: bool = False
    favorites: List[str] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

class UserCreate(BaseModel):
    email: EmailStr
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: UserRole = UserRole.BUYER

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None

# Property Models
class InvestmentDetails(BaseModel):
    rental_yield: float
    apy: float
    minimum_investment: float
    maximum_investment: Optional[float] = None
    exit_terms: str
    stay_eligibility: str
    guaranteed_returns: bool = False

class Property(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    title: str
    description: str
    property_type: PropertyType
    location: str
    price: float
    currency: Currency = Currency.NGN
    images: List[str] = []
    virtual_tour_url: Optional[str] = None
    investment_details: InvestmentDetails
    features: List[str] = []
    availability: str = "available"
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    square_feet: Optional[int] = None
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime] = None

class PropertyCreate(BaseModel):
    title: str
    description: str
    property_type: PropertyType
    location: str
    price: float
    currency: Currency = Currency.NGN
    images: List[str] = []
    virtual_tour_url: Optional[str] = None
    investment_details: InvestmentDetails
    features: List[str] = []
    availability: str = "available"
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    square_feet: Optional[int] = None

class PropertyUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    availability: Optional[str] = None
    images: Optional[List[str]] = None
    investment_details: Optional[InvestmentDetails] = None

class PropertyFilter(BaseModel):
    property_type: Optional[PropertyType] = None
    location: Optional[str] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    rental_yield_min: Optional[float] = None
    availability: Optional[str] = None

# Investment Models
class InstalmentPlan(BaseModel):
    total_amount: float
    down_payment: float
    monthly_payment: float
    duration_months: int
    total_instalments: int

class Investment(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    user_id: str
    property_id: str
    amount: float
    currency: Currency
    instalment_plan: Optional[InstalmentPlan] = None
    status: InvestmentStatus
    documents: List[str] = []
    initial_transaction_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

class InvestmentCreate(BaseModel):
    property_id: str
    amount: float
    currency: Currency
    use_instalment: bool = False
    down_payment_percentage: Optional[float] = None
    duration_months: Optional[int] = None

# Transaction Models
class TransactionStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"

class Transaction(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    user_id: str
    investment_id: Optional[str] = None
    reference: str
    amount: float
    currency: Currency
    status: TransactionStatus
    paystack_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    verified_at: Optional[datetime] = None

# OTP Models
class OTPVerification(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    contact: str
    code: str
    type: str
    expires_at: datetime
    verified: bool = False
    created_at: datetime

class SendOTPRequest(BaseModel):
    contact: str
    type: str

class VerifyOTPRequest(BaseModel):
    contact: str
    code: str
    type: str

# Auth Models
class LoginRequest(BaseModel):
    email: EmailStr
    otp_code: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User

# AI Models
class GenerateDescriptionRequest(BaseModel):
    title: str
    property_type: PropertyType
    location: str
    features: List[str]
    investment_details: InvestmentDetails

class RecommendationRequest(BaseModel):
    budget: float
    currency: Currency
    preferred_location: Optional[str] = None
    preferred_type: Optional[PropertyType] = None
    min_rental_yield: Optional[float] = None

class ChatRequest(BaseModel):
    message: str
    session_id: str
    user_id: Optional[str] = None

class InvestmentProjectionRequest(BaseModel):
    property_id: str
    investment_amount: float
    duration_years: int

# Payment Models
class PaymentInitializeRequest(BaseModel):
    email: str
    amount: float
    currency: Currency
    investment_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

# WhatsApp Models
class WhatsAppInquiryRequest(BaseModel):
    phone_number: str
    property_id: str
    message: str

class WhatsAppBookingRequest(BaseModel):
    phone_number: str
    property_id: str
    viewing_date: str
    viewing_time: str

# Calculator Models
class APYCalculatorRequest(BaseModel):
    principal_amount: float
    apy_rate: float
    duration_years: int

class InstalmentCalculatorRequest(BaseModel):
    total_amount: float
    down_payment_percentage: float
    duration_months: int
    interest_rate: float = 0.0
