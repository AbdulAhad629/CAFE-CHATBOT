import requests

r = requests.get('http://localhost:5000/staff/orders/all')

if r.status_code == 200:
    data = r.json()
    orders = data.get('data', [])
    
    print(f"\nAll {len(orders)} orders:\n")
    
    for order in orders:
        payment_id = order.get('payment_id')
        status = "✅ HAS" if payment_id else "❌ NONE"
        print(f"Order #{order['id']:2d} | Method: {order.get('payment_method', 'N/A'):10s} | {status} payment_id: {payment_id or 'NULL'}")
    
    # Count with payment_id
    with_payment = sum(1 for o in orders if o.get('payment_id'))
    print(f"\n{with_payment}/{len(orders)} orders have payment_id")
    
    if with_payment > 0:
        print("\n✅ PAYMENTS ARE BEING CREATED AND LINKED TO ORDERS!")
    else:
        print("\n⚠️  No payment_id found in orders")
else:
    print(f"Error: {r.status_code}")
