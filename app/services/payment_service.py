"""
Payment Service - WITH DATABASE PERSISTENCE
Location: app/services/payment_service.py

This payment system stores transactions in Supabase for real tracking.
Supports multiple payment methods with persistent storage.

For REAL implementation, replace with actual JazzCash/EasyPaisa API.
"""

import random
import time
from typing import Dict, Optional
from app.utils.supabase_client import supabase_client


class PaymentService:
    """
    Mock payment service for demonstration
    Simulates payment processing without actual transactions
    """
    
    def __init__(self):
        self.payment_methods = {
            'jazzcash': 'JazzCash Mobile Account',
            'easypaisa': 'EasyPaisa Mobile Account',
            'card': 'Credit/Debit Card',
            'cash': 'Cash on Pickup'
        }
        
        print("[OK] Payment Service initialized (DATABASE PERSISTENCE)")
    
    
    def create_payment(self, order_id: int, amount: float, 
                      payment_method: str = 'cash') -> Dict:
        """
        Create a payment transaction in Supabase database
        
        Args:
            order_id: Order ID
            amount: Amount in PKR
            payment_method: jazzcash/easypaisa/card/cash
            
        Returns:
            Payment details dict
        """
        
        try:
            # Create payment record in Supabase (uses only: order_id, amount, status)
            payment_data = {
                'order_id': order_id,
                'amount': amount,
                'status': 'pending'
            }
            
            # Insert into Supabase
            response = supabase_client.table('payments').insert(payment_data).execute()
            
            if response.data:
                payment = response.data[0]
                payment_id = payment.get('id', f"PAY-{order_id}")
                print(f"[PAYMENT] Payment created for Order #{order_id}: PKR {amount} ({payment_method})")
                return payment
            else:
                print(f"[PAYMENT] Failed to insert payment into database")
                return None
        
        except Exception as e:
            print(f"[PAYMENT] Error creating payment: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    
    def get_payment_url(self, payment_id: str) -> str:
        """
        Generate payment URL (mock)
        In real implementation, this would be JazzCash/EasyPaisa URL
        """
        
        payment = self.payments.get(payment_id)
        
        if not payment:
            return None
        
        method = payment['method']
        
        # Mock payment URLs
        urls = {
            'jazzcash': f"https://payments.jazzcash.com.pk/pay/{payment_id}",
            'easypaisa': f"https://easypaisa.com.pk/checkout/{payment_id}",
            'card': f"https://gateway.bank.pk/payment/{payment_id}",
            'cash': None  # No URL for cash
        }
        
        return urls.get(method)
    
    
    def simulate_payment_success(self, payment_id: str) -> bool:
        """
        Simulate successful payment and update in Supabase
        In real system, this would be callback from payment gateway
        """
        
        try:
            # Get current payment
            payment = self.get_payment_status(payment_id)
            
            if not payment:
                print(f"[PAYMENT] Payment {payment_id} not found")
                return False
            
            # Simulate processing delay
            time.sleep(1)
            
            # Random success (90% success rate for demo)
            success = random.random() < 0.9
            
            if success:
                # Update payment status in Supabase
                transaction_id = f"TXN-{random.randint(100000, 999999)}"
                update_data = {
                    'status': 'completed',
                    'transaction_id': transaction_id
                }
                
                supabase_client.table('payments').update(update_data).eq(
                    'payment_id', payment_id
                ).execute()
                
                print(f"[PAYMENT] ✅ Payment {payment_id} completed - TXN: {transaction_id}")
            else:
                # Mark as failed
                supabase_client.table('payments').update({
                    'status': 'failed'
                }).eq('payment_id', payment_id).execute()
                
                print(f"[PAYMENT] ❌ Payment {payment_id} failed")
            
            return success
            
        except Exception as e:
            print(f"[PAYMENT] Error updating payment: {str(e)}")
            return False
    
    
    def get_payment_status(self, payment_id: str) -> Optional[Dict]:
        """Get payment status from Supabase"""
        try:
            response = supabase_client.table('payments').select('*').eq(
                'payment_id', payment_id
            ).execute()
            
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"[PAYMENT] Error fetching payment status: {str(e)}")
            return None
    
    
    def format_payment_message(self, payment_id: str) -> str:
        """
        Format WhatsApp message for payment
        """
        
        try:
            payment = self.get_payment_status(payment_id)
            
            if not payment:
                return "Payment not found"
            
            method_name = self.payment_methods.get(payment['method'], 'Unknown')
            
            if payment['method'] == 'cash':
                message = f"""💰 Payment Details

Order ID: #{payment['order_id']}
Amount: PKR {payment['amount']}
Method: {method_name}

✅ Cash payment will be collected at pickup counter.

Thank you! 🙏"""
            
            else:
                payment_url = self.get_payment_url(payment_id)
                
                message = f"""💳 Payment Required

Order ID: #{payment['order_id']}
Amount: PKR {payment['amount']}
Method: {method_name}

Payment Link:
{payment_url}

⏰ Complete payment within 10 minutes.

For demo: Payment will auto-process in 1 minute."""
            
            return message
        
        except Exception as e:
            print(f"[PAYMENT] Error formatting message: {str(e)}")
            return "Payment message unavailable"
    
    
    def get_available_methods(self) -> Dict:
        """Get available payment methods"""
        return self.payment_methods


# Create singleton instance
payment_service = PaymentService()


# Test function
if __name__ == "__main__":
    print("\n" + "="*60)
    print("PAYMENT SERVICE TEST (DEMO MODE)")
    print("="*60)
    
    # Test payment creation
    payment = payment_service.create_payment(
        order_id=123,
        amount=500,
        payment_method='jazzcash'
    )
    
    print(f"\n✅ Payment created: {payment['payment_id']}")
    print(f"   Amount: PKR {payment['amount']}")
    print(f"   Method: {payment['method']}")
    
    # Get payment URL
    url = payment_service.get_payment_url(payment['payment_id'])
    print(f"\n🔗 Payment URL: {url}")
    
    # Simulate payment
    print("\n⏳ Simulating payment...")
    success = payment_service.simulate_payment_success(payment['payment_id'])
    
    if success:
        print("✅ Payment successful!")
    else:
        print("❌ Payment failed!")
    
    # Get status
    status = payment_service.get_payment_status(payment['payment_id'])
    print(f"\n📊 Final status: {status['status']}")
    
    # Format message
    message = payment_service.format_payment_message(payment['payment_id'])
    print(f"\n📱 WhatsApp Message:\n{message}")