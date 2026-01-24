#!/usr/bin/env python
"""
Direct database test - Check payments in Supabase
"""
from app.utils.supabase_client import supabase_client

print("\n" + "="*70)
print("📊 CHECKING PAYMENTS IN SUPABASE")
print("="*70 + "\n")

try:
    # Get all payments
    payments = supabase_client.table('payments').select('*').execute()
    
    print(f"Total payments: {len(payments.data)}\n")
    
    if payments.data:
        for p in payments.data[-5:]:  # Show last 5
            print(f"Payment ID: {p.get('payment_id')}")
            print(f"  Order ID: {p.get('order_id')}")
            print(f"  Amount: PKR {p.get('amount')}")
            print(f"  Method: {p.get('method')}")
            print(f"  Status: {p.get('status')}")
            print()
    
    # Check orders with payment_id
    orders = supabase_client.table('orders').select('id, total, payment_method, payment_id').execute()
    orders_with_payment = [o for o in orders.data if o.get('payment_id')]
    
    print(f"Orders with payment_id: {len(orders_with_payment)} out of {len(orders.data)}\n")
    
    if orders_with_payment:
        for o in orders_with_payment[-3:]:
            print(f"Order #{o['id']}")
            print(f"  Payment ID: {o.get('payment_id')}")
            print(f"  Method: {o.get('payment_method')}")
            print()

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
