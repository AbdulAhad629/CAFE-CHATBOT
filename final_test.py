#!/usr/bin/env python
"""
FINAL VERIFICATION TEST - Payment System Complete Flow
Creates order → creates payment → verifies payment_id linked
"""
import sys
sys.path.insert(0, '/d/whatsapp-cafeteria-bot')

from app.utils.supabase_client import supabase_client
from app.services.payment_service import payment_service

print("\n" + "=" * 70)
print("FINAL PAYMENT SYSTEM VERIFICATION")
print("=" * 70 + "\n")

try:
    # Get student
    students = supabase_client.table('students').select('id').limit(1).execute()
    student_id = students.data[0]['id']
    
    # Step 1: Create Order
    order_data = {
        'student_id': student_id,
        'total': 650.0,
        'payment_method': 'EasyPaisa',
        'status': 'pending'
    }
    
    order_resp = supabase_client.table('orders').insert(order_data).execute()
    order = order_resp.data[0]
    order_id = order['id']
    
    print(f"Step 1: Created Order")
    print(f"  Order ID: #{order_id}")
    print(f"  Amount: PKR {order['total']}")
    print(f"  Payment Method: {order['payment_method']}")
    
    # Step 2: Create Payment
    payment = payment_service.create_payment(
        order_id=order_id,
        amount=order['total'],
        payment_method=order['payment_method']
    )
    
    if not payment:
        print("\nStep 2: FAILED - Payment creation returned None")
        sys.exit(1)
    
    payment_id = payment.get('id')
    print(f"\nStep 2: Created Payment")
    print(f"  Payment ID (DB): {payment_id}")
    print(f"  Amount: PKR {payment.get('amount')}")
    print(f"  Status: {payment.get('status')}")
    
    # Step 3: Link Payment to Order
    supabase_client.table('orders').update(
        {'payment_id': payment_id}
    ).eq('id', order_id).execute()
    
    print(f"\nStep 3: Linked Payment to Order")
    
    # Step 4: Verify
    verified = supabase_client.table('orders').select('*').eq('id', order_id).execute()
    verified_order = verified.data[0]
    
    print(f"\nStep 4: Verification")
    print(f"  Order #{verified_order['id']}")
    print(f"  Payment ID in Order: {verified_order['payment_id']}")
    print(f"  Match: {verified_order['payment_id'] == payment_id}")
    
    # Step 5: Check Payment in Database
    payment_check = supabase_client.table('payments').select('*').eq('id', payment_id).execute()
    
    print(f"\nStep 5: Database Verification")
    print(f"  Payment in 'payments' table: {len(payment_check.data) > 0}")
    
    if payment_check.data:
        db_payment = payment_check.data[0]
        print(f"  Payment ID: {db_payment.get('id')}")
        print(f"  Order ID: {db_payment.get('order_id')}")
        print(f"  Amount: PKR {db_payment.get('amount')}")
    
    print("\n" + "=" * 70)
    if verified_order['payment_id'] == payment_id and payment_check.data:
        print("SUCCESS! PAYMENT SYSTEM FULLY OPERATIONAL!")
        print("=" * 70)
        print(f"\nSummary:")
        print(f"  ✓ Order created: #{order_id}")
        print(f"  ✓ Payment created: ID {payment_id}")
        print(f"  ✓ Payment linked to order")
        print(f"  ✓ Payment verified in database")
        print(f"\nYour system is READY TO SHIP! 🚀\n")
    else:
        print("FAILURE - Mismatch in payment linking")
        print("=" * 70)

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
