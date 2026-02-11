from fastapi import APIRouter, HTTPException, Depends
from models import GenerateDescriptionRequest, RecommendationRequest, ChatRequest, InvestmentProjectionRequest
from auth import db
from emergentintegrations.llm.chat import LlmChat, UserMessage
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/ai", tags=["ai"])

EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "")

@router.post("/generate-description")
async def generate_property_description(request: GenerateDescriptionRequest):
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id="property_description",
            system_message="You are a professional real estate investment copywriter. Create compelling, detailed property descriptions that highlight investment potential, rental yields, and key features."
        )
        chat.with_model("gemini", "gemini-3-flash-preview")
        
        prompt = f"""Generate a professional property description for:
        
Title: {request.title}
Type: {request.property_type}
Location: {request.location}
Features: {', '.join(request.features)}
Rental Yield: {request.investment_details.rental_yield}%
APY: {request.investment_details.apy}%
Exit Terms: {request.investment_details.exit_terms}
Stay Eligibility: {request.investment_details.stay_eligibility}

Create a compelling 2-3 paragraph description that appeals to investors."""
        
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        return {"description": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")

@router.post("/recommendations")
async def get_property_recommendations(request: RecommendationRequest):
    try:
        query = {}
        query["price"] = {"$lte": request.budget}
        if request.preferred_location:
            query["location"] = {"$regex": request.preferred_location, "$options": "i"}
        if request.preferred_type:
            query["property_type"] = request.preferred_type
        if request.min_rental_yield:
            query["investment_details.rental_yield"] = {"$gte": request.min_rental_yield}
        
        properties = await db.properties.find(query, {"_id": 0}).limit(10).to_list(length=10)
        
        if not properties:
            return {"recommendations": [], "message": "No properties match your criteria"}
        
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id="recommendations",
            system_message="You are an AI investment advisor for real estate. Analyze properties and provide personalized recommendations."
        )
        chat.with_model("gemini", "gemini-3-flash-preview")
        
        properties_summary = "\n".join([
            f"{i+1}. {p['title']} - {p['location']} - ₦{p['price']:,.0f} - {p['investment_details']['apy']}% APY"
            for i, p in enumerate(properties)
        ])
        
        prompt = f"""Based on the user's budget of {request.currency} {request.budget:,.0f}, here are the available properties:

{properties_summary}

Provide a brief analysis (2-3 sentences) recommending the top 3 properties and why they're good investment opportunities."""
        
        user_message = UserMessage(text=prompt)
        ai_analysis = await chat.send_message(user_message)
        
        return {
            "recommendations": properties[:5],
            "ai_analysis": ai_analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat")
async def ai_chatbot(request: ChatRequest):
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=request.session_id,
            system_message="""You are InvestAI Assistant, a knowledgeable real estate investment advisor for Oye Ekiti properties. 
            You help investors understand:
            - Rental yields and APY calculations
            - Investment strategies and risk management
            - Property features and benefits
            - Exit terms and resale options
            - Stay privileges and rental management
            
            Be professional, concise, and helpful. Always focus on investment value and returns."""
        )
        chat.with_model("gemini", "gemini-3-flash-preview")
        
        user_message = UserMessage(text=request.message)
        response = await chat.send_message(user_message)
        
        return {"response": response, "session_id": request.session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@router.post("/investment-projection")
async def generate_investment_projection(request: InvestmentProjectionRequest):
    try:
        property_doc = await db.properties.find_one({"id": request.property_id}, {"_id": 0})
        if not property_doc:
            raise HTTPException(status_code=404, detail="Property not found")
        
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id="investment_projection",
            system_message="You are a financial analyst specializing in real estate investment projections. Provide detailed, realistic projections with calculations."
        )
        chat.with_model("gemini", "gemini-3-flash-preview")
        
        apy = property_doc["investment_details"]["apy"]
        rental_yield = property_doc["investment_details"]["rental_yield"]
        
        prompt = f"""Generate an investment projection summary for:

Property: {property_doc['title']}
Investment Amount: ₦{request.investment_amount:,.0f}
Duration: {request.duration_years} years
APY: {apy}%
Rental Yield: {rental_yield}%

Provide:
1. Total expected returns
2. Year-by-year breakdown
3. Monthly passive income estimate
4. Exit value projection
5. Key investment highlights

Format as a clear, professional summary."""
        
        user_message = UserMessage(text=prompt)
        projection = await chat.send_message(user_message)
        
        return {
            "projection": projection,
            "property": property_doc,
            "parameters": {
                "investment_amount": request.investment_amount,
                "duration_years": request.duration_years,
                "apy": apy,
                "rental_yield": rental_yield
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
