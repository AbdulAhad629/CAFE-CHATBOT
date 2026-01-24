#!/usr/bin/env python
"""
SIMPLE PAYMENT TEST - Check if payment system works
"""
import subprocess
import time
import requests

print("\n" + "="*70)
print("🚀 PAYMENT SYSTEM TEST")
print("="*70)

# Kill existing Flask
print("\n1️⃣  Stopping Flask...")
subprocess.run(["taskkill", "/F", "/IM", "python.exe"], 
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)

# Start Flask with console output visible
print("2️⃣  Starting Flask server...\n")
flask_proc = subprocess.Popen(["python", "run.py"])
time.sleep(10)

# Check Flask
print("\n3️⃣  Checking Flask...")
try:
    r = requests.get("http://localhost:5000/staff/orders/all", timeout=3)
    print(f"   ✅ Flask responded: {r.status_code}\n")
except Exception as e:
    print(f"   ❌ Flask error: {str(e)}\n")
    flask_proc.terminate()
    exit(1)

# Create test order
print("4️⃣  Creating test order with payment...\n")
phone = "923001112333"
webhook = "http://localhost:5000/webhook/test-message"

msgs = ["menu", "1", "1 pizza", "checkout", "2", "yes"]

for msg in msgs:
    try:
        requests.post(webhook, json={"from": phone, "text": msg}, timeout=2)
    except:
        pass
    time.sleep(0.3)

time.sleep(2)

# Check result
print("5️⃣  Checking payment creation...\n")
try:
    r = requests.get("http://localhost:5000/staff/orders/all", timeout=2)
    orders = r.json().get('data', [])
    
    if orders:
        latest = orders[-1]
        print(f"Latest Order #{latest['id']}")
        print(f"  Amount: PKR {latest.get('total')}")
        print(f"  Method: {latest.get('payment_method')}")
        print(f"  Payment ID: {latest.get('payment_id')}")
        
        if latest.get('payment_id'):
            print("\n" + "="*70)
            print("✅ SUCCESS! PAYMENT CREATED!")
            print("="*70)
            print("\nPayments working! Ready to ship! 🚀\n")
        else:
            print("\n⚠️  No payment_id - check Flask console for errors\n")
except Exception as e:
    print(f"❌ Error: {e}\n")

# Clean up
print("Stopping Flask...")
flask_proc.terminate()
time.sleep(1)
print("✅ Done!\n")
