from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from datetime import datetime
from auth import get_current_user, db
import base64

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/investment/{investment_id}")
async def generate_investment_report(
    investment_id: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        # Get investment data
        investment = await db.investments.find_one({"id": investment_id}, {"_id": 0})
        if not investment:
            raise HTTPException(status_code=404, detail="Investment not found")
        
        if investment["user_id"] != current_user["id"] and current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get property data
        property_doc = await db.properties.find_one({"id": investment["property_id"]}, {"_id": 0})
        
        # Create PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#064E3B'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        # Title
        story.append(Paragraph("Investment Report", title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Investment Details
        story.append(Paragraph("<b>Investment Details</b>", styles['Heading2']))
        investment_data = [
            ['Investment ID:', investment['id']],
            ['Property:', property_doc.get('title', 'N/A')],
            ['Location:', property_doc.get('location', 'N/A')],
            ['Investment Amount:', f"₦{investment['amount']:,.2f}"],
            ['Currency:', investment['currency']],
            ['Status:', investment['status'].upper()],
            ['Date:', datetime.fromisoformat(investment['created_at']).strftime('%Y-%m-%d')]
        ]
        
        table = Table(investment_data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8F5E9')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        story.append(table)
        story.append(Spacer(1, 0.3*inch))
        
        # Property Investment Metrics
        story.append(Paragraph("<b>Investment Metrics</b>", styles['Heading2']))
        inv_details = property_doc.get('investment_details', {})
        metrics_data = [
            ['APY (Annual Percentage Yield):', f"{inv_details.get('apy', 0)}%"],
            ['Rental Yield:', f"{inv_details.get('rental_yield', 0)}%"],
            ['Minimum Investment:', f"₦{inv_details.get('minimum_investment', 0):,.2f}"],
            ['Guaranteed Returns:', 'Yes' if inv_details.get('guaranteed_returns') else 'No']
        ]
        
        metrics_table = Table(metrics_data, colWidths=[2*inch, 4*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#FFF3E0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        story.append(metrics_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Exit Terms
        story.append(Paragraph("<b>Exit Terms</b>", styles['Heading2']))
        story.append(Paragraph(inv_details.get('exit_terms', 'N/A'), styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Stay Eligibility
        story.append(Paragraph("<b>Stay Eligibility</b>", styles['Heading2']))
        story.append(Paragraph(inv_details.get('stay_eligibility', 'N/A'), styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Footer
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(
            f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>E1 Invest Real Estate Platform",
            footer_style
        ))
        
        # Build PDF
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        # Return PDF
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=investment_report_{investment_id}.pdf"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

@router.get("/property/{property_id}")
async def generate_property_brochure(
    property_id: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        property_doc = await db.properties.find_one({"id": property_id}, {"_id": 0})
        if not property_doc:
            raise HTTPException(status_code=404, detail="Property not found")
        
        # Create PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#064E3B'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        # Title
        story.append(Paragraph("Property Brochure", title_style))
        story.append(Paragraph(property_doc.get('title', 'N/A'), styles['Heading1']))
        story.append(Spacer(1, 0.3*inch))
        
        # Property Details
        property_data = [
            ['Location:', property_doc.get('location', 'N/A')],
            ['Type:', property_doc.get('property_type', 'N/A').replace('_', ' ').title()],
            ['Price:', f"₦{property_doc.get('price', 0):,.2f}"],
            ['Bedrooms:', str(property_doc.get('bedrooms', 'N/A'))],
            ['Bathrooms:', str(property_doc.get('bathrooms', 'N/A'))],
            ['Square Feet:', str(property_doc.get('square_feet', 'N/A'))],
        ]
        
        table = Table(property_data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8F5E9')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        story.append(table)
        story.append(Spacer(1, 0.3*inch))
        
        # Description
        story.append(Paragraph("<b>Description</b>", styles['Heading2']))
        story.append(Paragraph(property_doc.get('description', 'N/A'), styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Investment Metrics
        story.append(Paragraph("<b>Investment Opportunity</b>", styles['Heading2']))
        inv_details = property_doc.get('investment_details', {})
        metrics_data = [
            ['APY:', f"{inv_details.get('apy', 0)}%"],
            ['Rental Yield:', f"{inv_details.get('rental_yield', 0)}%"],
            ['Minimum Investment:', f"₦{inv_details.get('minimum_investment', 0):,.2f}"],
        ]
        
        metrics_table = Table(metrics_data, colWidths=[2*inch, 4*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FFF3E0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        story.append(metrics_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Features
        if property_doc.get('features'):
            story.append(Paragraph("<b>Features & Amenities</b>", styles['Heading2']))
            for feature in property_doc['features']:
                story.append(Paragraph(f"• {feature}", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=property_brochure_{property_id}.pdf"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")