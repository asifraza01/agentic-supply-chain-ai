"""
Generates realistic mock supplier contract PDFs for testing the RAG system.
"""
import os
from datetime import datetime, timedelta

# Create the contracts directory
os.makedirs("data/contracts", exist_ok=True)

# ============================================================================
# CONTRACT 1: Berlin Roasters (Coffee Supplier)
# ============================================================================
berlin_roasters_content = f"""
SUPPLIER AGREEMENT - BERLIN ROASTERS GmbH
==========================================

Contract Number: BR-2024-0892
Effective Date: January 1, 2024
Expiration Date: December 31, 2026

PARTIES:
--------
Supplier: Berlin Roasters GmbH
Address: Friedrichstraße 123, 10117 Berlin, Germany
Contact: procurement@berlinroasters.de

Buyer: [Your Company Name]
Address: [Your Address]

PRODUCTS COVERED:
-----------------
- SKU-107: Basmati Rice 1kg (Note: This is a test SKU mapping)
- SKU-108: Extra Virgin Olive Oil 500ml
- Coffee Beans (Various SKUs)

PRICING TERMS:
--------------
Unit prices are fixed for the contract duration with volume discounts:
- Orders 100-499 units: Standard price
- Orders 500-999 units: 5% discount
- Orders 1000+ units: 10% discount

DELIVERY & LEAD TIME:
---------------------
Standard Lead Time: 3 business days from order confirmation
Express Delivery: Available for 15% surcharge (1 business day)
Delivery Window: 8:00 AM - 6:00 PM, Monday-Friday

MINIMUM ORDER QUANTITY (MOQ):
-----------------------------
Minimum Order Quantity: 100 units per SKU
Mixed SKU orders accepted to meet MOQ

PAYMENT TERMS:
--------------
Net 30 days from invoice date
Early payment discount: 2% if paid within 10 days

PENALTIES & SERVICE LEVEL AGREEMENT (SLA):
------------------------------------------
- Late Delivery (1-2 days): 5% discount on affected order
- Late Delivery (3+ days): 10% discount + priority on next order
- Quality Defects: Full refund or replacement within 24 hours
- Stockout on Confirmed Order: Supplier pays 15% penalty

QUALITY STANDARDS:
------------------
All products must meet EU food safety regulations (EC 178/2002)
Certificates of Analysis required for each batch
Organic certification required for organic SKUs

TERMINATION CLAUSE:
-------------------
Either party may terminate with 90 days written notice
Immediate termination for material breach uncured within 30 days

Signed: ___________________ Date: {datetime.now().strftime('%Y-%m-%d')}
Berlin Roasters GmbH - Authorized Representative
"""

with open("data/contracts/berlin_roasters_contract.pdf.txt", "w") as f:
    f.write(berlin_roasters_content)

print("✅ Created: data/contracts/berlin_roasters_contract.pdf.txt")

# ============================================================================
# CONTRACT 2: Organic Dairy SLA (Milk Supplier)
# ============================================================================
organic_dairy_content = f"""
SERVICE LEVEL AGREEMENT - ORGANIC DAIRY COOPERATIVE
====================================================

Agreement Number: ODC-SLA-2024-156
Effective Date: March 1, 2024
Review Date: Annually on March 1

SUPPLIER INFORMATION:
---------------------
Organization: Organic Dairy Cooperative eG
Facility: Brandenburg Dairy Processing Center
Address: Milchstraße 45, 14482 Potsdam, Germany
Emergency Contact: +49 331 555-0123 (24/7)

PRODUCTS:
---------
- SKU-100: Organic Whole Milk 1L
- SKU-105: Greek Yogurt 500g
- SKU-109: Almond Milk Unsweetened 1L

INVENTORY & STOCK REQUIREMENTS:
-------------------------------
Supplier must maintain minimum safety stock of 500 units per SKU
at all times at the Brandenburg facility.

REORDER POINTS:
---------------
- SKU-100 (Organic Milk): Reorder when buyer inventory < 50 units
- SKU-105 (Greek Yogurt): Reorder when buyer inventory < 30 units
- SKU-109 (Almond Milk): Reorder when buyer inventory < 40 units

DELIVERY SCHEDULE:
------------------
Regular Deliveries: Tuesday and Friday of each week
Time Window: 6:00 AM - 10:00 AM (perishable goods priority)
Lead Time: 2 business days from order placement
Same-day delivery available for emergency orders (before 10 AM cutoff)

TEMPERATURE REQUIREMENTS:
-------------------------
All dairy products must be transported at 2-4°C
Temperature logs required for each delivery
Rejection policy: Any product >6°C upon arrival will be rejected

QUALITY ASSURANCE:
------------------
- Shelf life requirement: Minimum 14 days remaining on delivery
- Organic certification: EU Organic logo mandatory on all packaging
- Batch traceability: Full lot tracking required
- Microbiological testing: Weekly reports submitted to buyer

PENALTIES FOR NON-COMPLIANCE:
-----------------------------
1. Late Delivery:
   - 1 day late: 10% credit on order value
   - 2 days late: 20% credit on order value
   - 3+ days late: 50% credit + buyer may source elsewhere

2. Quality Failures:
   - Temperature breach: Full refund + 25% penalty
   - Expired/near-expiry: Full refund + replacement at supplier cost
   - Contamination: Full liability for damages + contract review

3. Stockout Situations:
   - Failure to deliver confirmed order: 30% penalty
   - Repeated stockouts (3+ in quarter): Contract termination right

FORCE MAJEURE:
--------------
Supplier not liable for delays due to:
- Natural disasters, extreme weather
- Government regulations or embargoes
- Labor strikes (if supplier notifies within 24 hours)

CONTINUITY PLANNING:
--------------------
Supplier must maintain backup production capacity of 150%
Alternative delivery routes must be established
Business continuity plan to be shared annually

PRICING ADJUSTMENT:
-------------------
Prices fixed for 12 months
Annual adjustment based on German Dairy Index (max 5% increase)
Emergency surcharges require 14-day notice

Signed: ___________________ Date: {datetime.now().strftime('%Y-%m-%d')}
Organic Dairy Cooperative - Quality Assurance Director
"""

with open("data/contracts/organic_dairy_sla.pdf.txt", "w") as f:
    f.write(organic_dairy_content)

print("✅ Created: data/contracts/organic_dairy_sla.pdf.txt")

# ============================================================================
# CONTRACT 3: Historical Stockout Analysis Report
# ============================================================================
stockout_report_content = f"""
INCIDENT ANALYSIS REPORT - SUPPLY CHAIN DISRUPTIONS
====================================================

Report ID: SCR-2025-Q4-001
Date: {datetime.now().strftime('%Y-%m-%d')}
Prepared By: Supply Chain Analytics Team
Classification: Internal Use Only

EXECUTIVE SUMMARY:
------------------
This report analyzes three major stockout incidents in Q4 2025 affecting
high-velocity SKUs in our Berlin retail network. Root causes and preventive
measures are documented to prevent recurrence.

INCIDENT #1: ORGANIC MILK STOCKOUT (SKU-100)
--------------------------------------------
Date Range: November 12-18, 2025
Affected Stores: Store #4, Store #7, Store #9
Duration: 6 days
Revenue Impact: €23,450 lost sales

TIMELINE:
Nov 10: Supplier (Organic Dairy Coop) reported production delay
Nov 11: Inventory at Store #4 dropped to 15 units (below reorder point)
Nov 12: Complete stockout at Store #4
Nov 13-15: Stockout spread to Stores #7 and #9
Nov 16: Emergency delivery arranged (express surcharge: €450)
Nov 18: Normal inventory levels restored

ROOT CAUSE ANALYSIS:
1. Primary Cause: Supplier production equipment failure
2. Contributing Factor: Safety stock calculation did not account for
   single-supplier dependency risk
3. System Failure: Automated reorder system did not trigger emergency
   procurement protocols when supplier confirmed delay

LESSONS LEARNED:
- Need for secondary supplier qualification for critical SKUs
- Safety stock should be increased from 5 days to 10 days for single-source items
- Automated alerts should escalate to management when supplier confirms delay

INCIDENT #2: GREEK YOGURT EXPIRY WASTE (SKU-105)
-------------------------------------------------
Date: October 28, 2025
Affected Stores: Store #2, Store #5
Product Waste: 340 units (€2,890 value)

ROOT CAUSE:
- Demand forecasting model overestimated sales by 340%
- Promotional campaign was cancelled but inventory order was not adjusted
- No automated alert for slow-moving perishable inventory

RECOMMENDATIONS:
- Implement dynamic safety stock adjustment based on promotion calendar
- Add "perishable goods" flag requiring manual review for orders >200 units
- Create automated markdown protocol for items with <7 days shelf life

INCIDENT #3: ALMOND MILK SUPPLIER DELAY (SKU-109)
--------------------------------------------------
Date Range: December 3-8, 2025
Affected Stores: All 10 stores
Delay Duration: 5 days
Customer Complaints: 47 logged

ROOT CAUSE:
- Supplier (Berlin Roasters) experienced raw material shortage
- Contract lead time of 3 days was insufficient for supply chain volatility
- No real-time visibility into supplier's raw material inventory

CORRECTIVE ACTIONS:
- Renegotiated contract to include supplier inventory transparency clause
- Increased lead time buffer from 3 days to 5 days for imported ingredients
- Implemented weekly supplier capacity check-ins during high-demand periods

OVERALL RECOMMENDATIONS FOR 2026:
----------------------------------
1. DIVERSIFICATION: Qualify backup suppliers for all SKUs with >€50K annual revenue
2. SAFETY STOCK: Increase from 5 days to 7-10 days for single-source items
3. MONITORING: Implement real-time supplier risk scoring system
4. AUTOMATION: Enhance LangGraph agent to check supplier capacity before ordering
5. COMMUNICATION: Establish direct API integration with top 3 suppliers

FINANCIAL IMPACT SUMMARY:
-------------------------
Total Lost Revenue: €26,340
Total Penalties Collected from Suppliers: €8,200
Net Impact: €18,140
Prevention Investment Needed: €45,000 (supplier diversification program)
ROI of Prevention: 248% (based on avoiding repeat incidents)

APPROVAL:
---------
Reviewed by: Maria Schmidt, Head of Supply Chain
Date: {datetime.now().strftime('%Y-%m-%d')}
Next Review: Q1 2026
"""

with open("data/contracts/historical_stockout_report_2025.pdf.txt", "w") as f:
    f.write(stockout_report_content)

print("✅ Created: data/contracts/historical_stockout_report_2025.pdf.txt")

print("\n" + "="*60)
print("🎉 All mock PDF contracts generated successfully!")
print("="*60)
print(f"📂 Location: data/contracts/")
print(f"📄 Files created: 3 documents")
print(f"\nThese .txt files simulate PDF content for RAG testing.")
print("In production, you would use actual PDFs with LlamaParse.")