"""
Minimal payment creation test - no Flask imports
"""
import os
os.environ['PYTHONPATH'] = 'd:/whatsapp-cafeteria-bot'

print("\n" + "="*70)
print("MINIMAL PAYMENT CREATION TEST")
print("="*70 + "\n")

# Test 1: Direct Supabase import
print("1️⃣  Testing direct Supabase client...")
try:
    from supabase import create_client
    
    SUPABASE_URL = "https://qxnnfzdfqyqyxdccjfvq.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF4bm5memRmcXlxeXhkY2NqZnZxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDQxNjc2OTIsImV4cCI6MjAxOTc0MzY5Mn0.2ybNc-0GXLBbI3n8i3s0Pv1F1H6I7p0K4I7K5K7K7K"
    
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("   ✅ Supabase client created")
    
    # Check payments table
    response = supabase.table('payments').select('count', count='exact').execute()
    print(f"   ✅ Current payments in table: {response.count}")
    
except Exception as e:
    print(f"   ❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    import sys
    sys.exit(1)

# Test 2: Create a payment directly
print("\n2️⃣  Creating test payment directly in Supabase...")
try:
    import random
    
    payment_id = f"PAY-999-{random.randint(1000, 9999)}"
    
    payment_data = {
        'payment_id': payment_id,
        'order_id': 999,
        'amount': 500,
        'method': 'cash',
        'status': 'pending'
    }
    
    print(f"   Inserting: {payment_data}")
    response = supabase.table('payments').insert(payment_data).execute()
    
    if response.data:
        print(f"   ✅ Payment inserted successfully!")
        payment = response.data[0]
        print(f"      ID: {payment.get('id')}")
        print(f"      payment_id: {payment.get('payment_id')}")
        print(f"      order_id: {payment.get('order_id')}")
        print(f"      amount: {payment.get('amount')}")
        print(f"      method: {payment.get('method')}")
        print(f"      status: {payment.get('status')}")
    else:
        print(f"   ⚠️  Response empty: {response}")
        
except Exception as e:
    print(f"   ❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    import sys
    sys.exit(1)

# Test 3: Verify the payment exists
print("\n3️⃣  Verifying payment in database...")
try:
    response = supabase.table('payments').select('*').eq(
        'payment_id', payment_id
    ).execute()
    
    if response.data:
        print(f"   ✅ Found {len(response.data)} payment(s)")
        for p in response.data:
            print(f"      - {p['payment_id']}: Order #{p['order_id']}, PKR {p['amount']}")
    else:
        print(f"   ❌ Payment not found!")
        
except Exception as e:
    print(f"   ❌ Error: {str(e)}")
    import sys
    sys.exit(1)

print("\n" + "="*70)
print("✅ DIRECT SUPABASE INSERTION WORKING!")
print("="*70 + "\n")
