"""
Verify payments in Supabase after order creation
"""

# Use venv python which has proper websockets
from supabase import create_client

SUPABASE_URL = "https://qxnnfzdfqyqyxdccjfvq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF4bm5memRmcXlxeXhkY2NqZnZxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDQxNjc2OTIsImV4cCI6MjAxOTc0MzY5Mn0.2ybNc-0GXLBbI3n8i3s0Pv1F1H6I7p0K4I7K5K7K7K"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("\n" + "="*70)
print("  VERIFYING PAYMENTS IN SUPABASE")
print("="*70 + "\n")

try:
    # Fetch all payments
    response = supabase.table('payments').select('*').order('id', desc=True).execute()
    
    payments = response.data
    print(f"Total payments in database: {len(payments)}\n")
    
    if payments:
        print("Recent Payments:")
        print("-" * 70)
        
        for payment in payments[:10]:  # Show last 10
            print(f"\nPayment ID: {payment.get('payment_id')}")
            print(f"  Order ID: #{payment.get('order_id')}")
            print(f"  Amount: PKR {payment.get('amount')}")
            print(f"  Method: {payment.get('method').upper()}")
            print(f"  Status: {payment.get('status').upper()}")
            print(f"  Created: {payment.get('created_at', 'N/A')[:10]}")
        
        print("\n" + "-" * 70)
        print(f"\n✅ PAYMENTS ARE NOW BEING SAVED TO SUPABASE!")
        
        # Summary
        methods = {}
        total_amount = 0
        for p in payments:
            method = p.get('method', 'unknown').upper()
            methods[method] = methods.get(method, 0) + 1
            total_amount += p.get('amount', 0)
        
        print(f"\nSummary:")
        print(f"  Total Amount: PKR {total_amount}")
        print(f"  By Method: {methods}")
    else:
        print("No payments found yet - orders may not have payment methods enabled")

except Exception as e:
    print(f"Error: {str(e)}")

print("\n" + "="*70 + "\n")
