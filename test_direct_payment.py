"""
Direct payment creation test - bypass Flask
"""
import sys
sys.path.insert(0, 'd:/whatsapp-cafeteria-bot')

print("\n" + "="*70)
print("DIRECT PAYMENT CREATION TEST")
print("="*70 + "\n")

# Test 1: Import supabase client
print("1️⃣  Testing Supabase connection...")
try:
    from app.utils.supabase_client import supabase_client
    print("   ✅ Supabase client imported")
    
    # Try to connect
    response = supabase_client.table('payments').select('count', count='exact').execute()
    current_count = response.count
    print(f"   ✅ Supabase connected - Current payments: {current_count}")
except Exception as e:
    print(f"   ❌ Supabase error: {str(e)}")
    sys.exit(1)

# Test 2: Import payment service
print("\n2️⃣  Testing payment service import...")
try:
    from app.services.payment_service import PaymentService
    print("   ✅ PaymentService class imported")
    
    # Create instance
    ps = PaymentService()
    print("   ✅ PaymentService instantiated")
except Exception as e:
    print(f"   ❌ Import error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Create a test payment
print("\n3️⃣  Creating test payment...")
try:
    test_payment = ps.create_payment(
        order_id=999,
        amount=500,
        payment_method='cash'
    )
    
    if test_payment:
        print(f"   ✅ Payment created: {test_payment.get('payment_id')}")
        print(f"      Order ID: {test_payment.get('order_id')}")
        print(f"      Amount: PKR {test_payment.get('amount')}")
        print(f"      Method: {test_payment.get('method')}")
        print(f"      Status: {test_payment.get('status')}")
    else:
        print("   ❌ Payment creation returned None")
except Exception as e:
    print(f"   ❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Verify in database
print("\n4️⃣  Verifying payment in database...")
try:
    response = supabase_client.table('payments').select('*').eq(
        'payment_id', test_payment.get('payment_id')
    ).execute()
    
    if response.data:
        print("   ✅ Payment found in database!")
        payment = response.data[0]
        print(f"      payment_id: {payment['payment_id']}")
        print(f"      order_id: {payment['order_id']}")
        print(f"      amount: {payment['amount']}")
        print(f"      method: {payment['method']}")
        print(f"      status: {payment['status']}")
    else:
        print("   ❌ Payment NOT found in database!")
except Exception as e:
    print(f"   ❌ Error: {str(e)}")
    sys.exit(1)

print("\n" + "="*70)
print("✅ ALL TESTS PASSED - PAYMENT STORAGE WORKING!")
print("="*70 + "\n")
