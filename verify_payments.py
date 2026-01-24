"""
Direct payment verification using Supabase client
"""

import sys
sys.path.insert(0, 'd:/whatsapp-cafeteria-bot')

from supabase import create_client

# Initialize Supabase
SUPABASE_URL = "https://qxnnfzdfqyqyxdccjfvq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF4bm5memRmcXlxeXhkY2NqZnZxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDQxNjc2OTIsImV4cCI6MjAxOTc0MzY5Mn0.2ybNc-0GXLBbI3n8i3s0Pv1F1H6I7p0K4I7K5K7K7K"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("\n" + "="*70)
print("  PAYMENT DATABASE VERIFICATION")
print("="*70 + "\n")

try:
    # Fetch all payments
    print("📊 Fetching payments from Supabase...\n")
    response = supabase.table('payments').select('*').execute()
    
    payments = response.data
    print(f"✅ Total Payments in Database: {len(payments)}\n")
    
    if payments:
        print("Payment Details:")
        print("-" * 70)
        
        for i, payment in enumerate(payments, 1):
            print(f"\n{i}. Payment ID: {payment.get('payment_id')}")
            print(f"   Order ID: #{payment.get('order_id')}")
            print(f"   Amount: PKR {payment.get('amount')}")
            print(f"   Method: {payment.get('method').upper()}")
            print(f"   Status: {payment.get('status').upper()}")
            
            if payment.get('created_at'):
                print(f"   Created: {payment.get('created_at')}")
        
        print("\n" + "-" * 70)
        
        # Summary statistics
        print("\n📈 PAYMENT SUMMARY:")
        
        # By method
        methods = {}
        total_amount = 0
        
        for payment in payments:
            method = payment.get('method', 'unknown').upper()
            amount = payment.get('amount', 0)
            methods[method] = methods.get(method, 0) + 1
            total_amount += amount
        
        print(f"\n   Payment Methods:")
        for method in sorted(methods.keys()):
            print(f"      • {method}: {methods[method]} payment(s)")
        
        print(f"\n   Total Amount: PKR {total_amount}")
        
        # By status
        statuses = {}
        for payment in payments:
            status = payment.get('status', 'unknown').upper()
            statuses[status] = statuses.get(status, 0) + 1
        
        print(f"\n   Payment Status:")
        for status in sorted(statuses.keys()):
            print(f"      • {status}: {statuses[status]} payment(s)")
        
        print("\n✅ PAYMENTS ARE STORED IN SUPABASE DATABASE!")
        
    else:
        print("⚠️  No payments found in database.")
        print("    They will be created when new orders are placed.")

except Exception as e:
    print(f"❌ Error: {str(e)}")

print("\n" + "="*70 + "\n")
