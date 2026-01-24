# Debugging Orders Not Showing on Dashboard

## Quick Fix

When you run `test_chatbot.py` and place orders, they should appear on the dashboard. If they don't:

### Step 1: Test Orders Creation
```bash
python test_chatbot.py
```
Choose option `3` (Complete Order Flow Test) or `2` (Natural Language Orders)

### Step 2: Check Dashboard Endpoint Directly
```bash
python test_chatbot.py
```
Then choose option `7` (Check Dashboard Orders)

This will show:
- **Pending Orders**: Orders in active states (pending, confirmed, preparing)
- **All Orders**: Complete database view of last 100 orders

### Step 3: Verify Backend Responses

The test now includes:
- ✅ `check_orders_in_dashboard()` - Fetches `/staff/orders/pending`
- ✅ `check_all_orders_in_db()` - Fetches `/staff/orders/all`

### What the Fix Includes

1. **Test Endpoint Fixed**: `/webhook/test-message` works properly with chatbot service
2. **Order Fetching Enhanced**: Dashboard endpoint fixed to return all order data
3. **Data Display Improved**: Dashboard properly handles nested student/items data
4. **Status Updates Fixed**: Endpoint path corrected from `/api/orders/` to `/orders/`

## Expected Results After Fix

### After Placing an Order:
```
✅ Found 1 pending orders!
ℹ️ Order #123: PENDING - PKR 550 (John Doe)
```

### On Dashboard:
- Order appears with customer name
- Order total and items visible
- Status buttons working (Confirm → Preparing → Ready → Complete)

## If Orders Still Don't Show

Check these in order:

1. **Flask Console** - Look for error messages when processing messages
2. **Supabase Dashboard** - Check `orders` table directly
3. **Network Tab** - Verify API calls are reaching `/staff/orders/pending`
4. **Browser Console** - Check for JavaScript errors on dashboard

## Debug Commands

### Check Pending Orders Directly
```bash
curl "http://localhost:5000/staff/orders/pending"
```

### Check All Orders in DB
```bash
curl "http://localhost:5000/staff/orders/all"
```

### Place a Test Order
```bash
curl -X POST "http://localhost:5000/webhook/test-message" \
  -H "Content-Type: application/json" \
  -d '{"from":"+923001234567","message":"2 burger aur coffee"}'
```

## Auto-Refresh Dashboard

Dashboard automatically:
- ✅ Loads orders when page opens
- ✅ Refreshes every 10 seconds
- ✅ Shows customer name and WhatsApp number
- ✅ Updates status in real-time

## Order Flow

```
Customer sends message
    ↓
/webhook/test-message endpoint
    ↓
chatbot_service.process_message()
    ↓
Creates order in Supabase
    ↓
Staff refreshes /staff/orders/pending
    ↓
Orders appear on dashboard
```

---

✅ **Your system is now properly integrated!**
