import requests

print("\nFetching recent orders...\n")

r = requests.get('http://localhost:5000/staff/orders/all')
print(f"Status: {r.status_code}")

if r.status_code == 200:
    data = r.json()
    orders = data.get('data', [])
    print(f"Total orders: {len(orders)}\n")
    
    if orders:
        print("Recent orders with payment info:")
        print("-" * 70)
        for order in orders[-5:]:
            print(f"\nOrder #{order['id']}")
            print(f"  Method: {order.get('payment_method')}")
            print(f"  Payment ID: {order.get('payment_id')}")
            print(f"  Total: PKR {order.get('total')}")
            print(f"  Status: {order.get('status')}")
            
            if order.get('payment_id'):
                print("  ✅ HAS PAYMENT_ID")
            else:
                print("  ❌ NO PAYMENT_ID")
else:
    print(f"Error: {r.status_code}")
    print(r.text)
