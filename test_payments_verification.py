"""
PAYMENT DATABASE VERIFICATION TEST
Verify that payments are being stored in Supabase
"""

import requests
import json
from app.utils.supabase_client import supabase_client

print("\n" + "="*70)
print("  PAYMENT STORAGE VERIFICATION")
print("="*70 + "\n")

try:
    # Fetch all payments from Supabase
    print("📊 Fetching payments from Supabase...")
    response = supabase_client.table('payments').select('*').execute()
    
    payments = response.data
    print(f"\n✅ Total Payments in Database: {len(payments)}\n")
    
    if payments:
        print("Payment Details:")
        print("-" * 70)
        
        for payment in payments:
            print(f"\n💳 Payment ID: {payment.get('payment_id', 'N/A')}")
            print(f"   Order ID: #{payment.get('order_id', 'N/A')}")
            print(f"   Amount: PKR {payment.get('amount', 0)}")
            print(f"   Method: {payment.get('method', 'N/A').upper()}")
            print(f"   Status: {payment.get('status', 'N/A').upper()}")
            
            # Check created_at if available
            if payment.get('created_at'):
                print(f"   Created: {payment.get('created_at')}")
            
            # Check transaction_id if payment completed
            if payment.get('transaction_id'):
                print(f"   Transaction ID: {payment.get('transaction_id')}")
        
        print("\n" + "-" * 70)
        
        # Payment summary
        print("\n📈 PAYMENT SUMMARY:")
        print(f"   Total Payments: {len(payments)}")
        
        # Count by method
        methods = {}
        total_amount = 0
        
        for payment in payments:
            method = payment.get('method', 'unknown').upper()
            amount = payment.get('amount', 0)
            
            methods[method] = methods.get(method, 0) + 1
            total_amount += amount
        
        print(f"\n   By Payment Method:")
        for method, count in sorted(methods.items()):
            print(f"      • {method}: {count} payment(s)")
        
        print(f"\n   Total Amount: PKR {total_amount}")
        
        # Count by status
        statuses = {}
        for payment in payments:
            status = payment.get('status', 'unknown').upper()
            statuses[status] = statuses.get(status, 0) + 1
        
        print(f"\n   By Status:")
        for status, count in sorted(statuses.items()):
            print(f"      • {status}: {count} payment(s)")
        
        # Check link with orders
        print(f"\n🔗 PAYMENT-ORDER RELATIONSHIP:")
        
        # Get all orders
        orders_response = supabase_client.table('orders').select('*').execute()
        orders = orders_response.data
        
        orders_with_payment = 0
        for order in orders:
            if order.get('payment_id'):
                orders_with_payment += 1
                # Find matching payment
                for payment in payments:
                    if payment.get('payment_id') == order.get('payment_id'):
                        print(f"   ✅ Order #{order['id']} → Payment {payment['payment_id']} ({payment.get('status')})")
                        break
        
        print(f"\n   Total Orders with Payments: {orders_with_payment}/{len(orders)}")
        
        print("\n✅ PAYMENTS ARE BEING STORED IN SUPABASE!")
        
    else:
        print("❌ No payments found in database yet.")
        print("   Payments will be created when orders are placed.")

except Exception as e:
    print(f"\n❌ Error fetching payments: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70 + "\n")
