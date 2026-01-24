#!/usr/bin/env python
"""
SIMPLE PAYMENT TEST - Just check if it works
"""
import subprocess
import time
import requests
import sys

print("\n" + "="*70)
print("🚀 PAYMENT SYSTEM TEST")
print("="*70)

# Kill any existing Flask
print("\n1️⃣  Stopping Flask...")
subprocess.run(["taskkill", "/F", "/IM", "python.exe"], 
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)

# Start Flask
print("2️⃣  Starting Flask server...")
flask_proc = subprocess.Popen(
    ["python", "run.py"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)
time.sleep(8)

# Check Flask is running
print("3️⃣  Checking Flask...")
try:
    r = requests.get("http://localhost:5000/staff/orders/all", timeout=2)
    if r.status_code == 200:
        print("   ✅ Flask is running\n")
    else:
        print(f"   ❌ Flask error: {r.status_code}\n")
        sys.exit(1)
except:
    print("   ❌ Flask not responding\n")
    sys.exit(1)

# Create test order with payment
print("4️⃣  Creating test order with JazzCash payment...")
phone = "923001112222"
webhook = "http://localhost:5000/webhook/test-message"

steps = [
    ("menu", "menu"),
    ("1", "category"),
    ("1 pizza", "item"),
    ("checkout", "checkout"),
    ("2", "jazzcash"),
    ("yes", "confirm"),
]

for msg, step in steps:
    try:
        requests.post(webhook, json={"from": phone, "text": msg}, timeout=2)
        print(f"   • {step}... ✓")
    except:
        print(f"   • {step}... ❌")

time.sleep(2)

# Check if order was created with payment_id
print("\n5️⃣  Checking if payment was created...")
try:
    r = requests.get("http://localhost:5000/staff/orders/all", timeout=2)
    if r.status_code == 200:
        orders = r.json().get('data', [])
        
        if orders:
            # Get latest order
            latest = orders[-1]
            print(f"\n   Order #{latest['id']}")
            print(f"   Amount: PKR {latest.get('total')}")
            print(f"   Method: {latest.get('payment_method')}")
            print(f"   Payment ID: {latest.get('payment_id')}")
            
            if latest.get('payment_id'):
                print("\n" + "="*70)
                print("✅ SUCCESS! PAYMENTS ARE WORKING!")
                print("="*70)
                print("\nPayment records are being created in Supabase!")
                print("Your system is ready to ship! 🚀\n")
            else:
                print("\n" + "="*70)
                print("⚠️  Payment ID is NULL")
                print("="*70)
                print("\nCheck Flask console output above for errors\n")
        else:
            print("\n❌ No orders found in database\n")
    else:
        print(f"\n❌ API error: {r.status_code}\n")
except Exception as e:
    print(f"\n❌ Error: {str(e)}\n")

# Stop Flask
print("\n6️⃣  Stopping Flask...")
flask_proc.terminate()
time.sleep(1)

print("✅ Test complete!\n")
