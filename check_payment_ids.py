import requests

r = requests.get('http://localhost:5000/api/orders')
orders = r.json().get('data', [])
print(f'Total orders: {len(orders)}')
if orders:
    print(f'\nRecent orders with payment_id:')
    for order in orders[-3:]:
        print(f"  Order #{order['id']}: payment_id = {order.get('payment_id')}")
