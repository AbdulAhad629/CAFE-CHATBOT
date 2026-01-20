"""
Notification Service
Handles sending notifications to users and staff
"""
from app.services.whatsapp_service import whatsapp_service
from app.utils.supabase_client import supabase_client
from typing import Dict, Optional


class NotificationService:
    """
    Manages all notifications for orders and updates
    """
    
    def __init__(self):
        self.whatsapp = whatsapp_service
        self.supabase = supabase_client
    
    
    def notify_order_placed(self, order_id: int, to_number: str) -> bool:
        """
        Send notification when order is placed
        
        Args:
            order_id: Order ID
            to_number: User's WhatsApp number
        """
        try:
            # Get order details
            order = self._get_order_details(order_id)
            
            if not order:
                return False
            
            message = f"✅ Order Confirmed!\n\n"
            message += f"🔖 Order ID: #{order_id}\n"
            message += f"💰 Total: PKR {order['total']}\n"
            message += f"📍 Status: {order['status'].upper()}\n\n"
            message += f"Your order is being prepared! 👨‍🍳\n"
            message += f"We'll notify you when it's ready.\n\n"
            message += f"Type 'track {order_id}' to check status anytime."
            
            self.whatsapp.send_text_message(to_number, message)
            return True
            
        except Exception as e:
            print(f"Error sending order placed notification: {str(e)}")
            return False
    
    
    def notify_order_status_change(self, order_id: int, new_status: str) -> bool:
        """
        Send notification when order status changes
        
        Args:
            order_id: Order ID
            new_status: New status (preparing, ready, completed)
        """
        try:
            # Get order with student info
            order = self._get_order_with_student(order_id)
            
            if not order or not order.get('students'):
                print(f"Order {order_id} or student not found")
                return False
            
            student = order['students']
            whatsapp_number = student.get('whatsapp_number')
            
            if not whatsapp_number:
                print(f"No WhatsApp number for student")
                return False
            
            # Create appropriate message based on status
            if new_status == 'preparing':
                message = f"👨‍🍳 Your Order #{order_id} is now being prepared!\n\n"
                message += f"We're working on it right now. 🔥"
                
            elif new_status == 'ready':
                message = f"🎉 Great News!\n\n"
                message += f"Your Order #{order_id} is READY for pickup! 🥳\n\n"
                message += f"📍 Please collect from the counter.\n"
                message += f"💰 Total: PKR {order['total']}\n\n"
                message += f"Thank you for ordering! 🙏"
                
            elif new_status == 'completed':
                message = f"✅ Order #{order_id} Completed!\n\n"
                message += f"Thank you for your order! 😊\n"
                message += f"We hope you enjoyed your meal! 🍴\n\n"
                message += f"Order again anytime by typing 'menu'"
                
            elif new_status == 'cancelled':
                message = f"❌ Order #{order_id} has been cancelled.\n\n"
                message += f"If you have any questions, please contact the café.\n"
                message += f"You can place a new order anytime by typing 'menu'."
                
            else:
                message = f"📦 Order #{order_id} Status Update\n\n"
                message += f"Status: {new_status.upper()}"
            
            # Send notification
            self.whatsapp.send_text_message(whatsapp_number, message)
            print(f"✅ Notification sent to {whatsapp_number} for order {order_id}")
            return True
            
        except Exception as e:
            print(f"Error sending status change notification: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    
    def notify_staff_new_order(self, order_id: int) -> bool:
        """
        Notify staff about new order (can be extended to send to staff WhatsApp group)
        
        Args:
            order_id: New order ID
        """
        try:
            # Get order details with items
            order = self._get_order_with_items(order_id)
            
            if not order:
                return False
            
            # Log to console for now
            print("\n" + "="*60)
            print("🔔 NEW ORDER ALERT!")
            print("="*60)
            print(f"Order ID: #{order_id}")
            print(f"Total: PKR {order['total']}")
            print(f"Items:")
            
            for item in order.get('order_items', []):
                menu_item = item.get('menu_items', {})
                print(f"  - {item['quantity']}x {menu_item.get('name', 'Unknown')}")
            
            print("="*60 + "\n")
            
            # TODO: Send to staff WhatsApp group or specific numbers
            # Example:
            # staff_numbers = ["+923001111111", "+923002222222"]
            # for number in staff_numbers:
            #     self.whatsapp.send_text_message(number, staff_message)
            
            return True
            
        except Exception as e:
            print(f"Error notifying staff: {str(e)}")
            return False
    
    
    def send_order_tracking_info(self, to_number: str, order_id: int) -> bool:
        """
        Send current order status to user
        
        Args:
            to_number: User's WhatsApp number
            order_id: Order ID to track
        """
        try:
            order = self._get_order_with_items(order_id)
            
            if not order:
                self.whatsapp.send_text_message(
                    to_number,
                    f"❌ Order #{order_id} not found.\n\nPlease check the order number and try again."
                )
                return False
            
            # Create status message
            status_emoji = {
                'pending': '⏳',
                'confirmed': '✅',
                'preparing': '👨‍🍳',
                'ready': '🎉',
                'completed': '✅',
                'cancelled': '❌'
            }
            
            current_status = order['status']
            emoji = status_emoji.get(current_status, '📦')
            
            message = f"📍 Order Tracking\n\n"
            message += f"🔖 Order ID: #{order_id}\n"
            message += f"{emoji} Status: {current_status.upper()}\n"
            message += f"💰 Total: PKR {order['total']}\n\n"
            
            message += "📦 Items:\n"
            for item in order.get('order_items', []):
                menu_item = item.get('menu_items', {})
                message += f"  • {item['quantity']}x {menu_item.get('name', 'Item')}\n"
            
            message += f"\n"
            
            # Add status-specific message
            if current_status == 'pending':
                message += "⏳ Your order is in queue and will be processed soon."
            elif current_status == 'confirmed':
                message += "✅ Your order has been confirmed!"
            elif current_status == 'preparing':
                message += "👨‍🍳 Your order is being prepared right now!"
            elif current_status == 'ready':
                message += "🎉 Your order is ready for pickup at the counter!"
            elif current_status == 'completed':
                message += "✅ Order completed. Thank you!"
            elif current_status == 'cancelled':
                message += "❌ This order was cancelled."
            
            self.whatsapp.send_text_message(to_number, message)
            return True
            
        except Exception as e:
            print(f"Error sending tracking info: {str(e)}")
            return False
    
    
    def send_daily_summary_to_staff(self) -> bool:
        """
        Send daily summary to staff (can be scheduled)
        """
        try:
            from datetime import datetime, timedelta
            
            today = datetime.now().date()
            
            # Get today's completed orders
            response = self.supabase.table('orders').select(
                '*, order_items(*)'
            ).gte('created_at', f'{today}T00:00:00').lte(
                'created_at', f'{today}T23:59:59'
            ).execute()
            
            orders = response.data
            
            total_orders = len(orders)
            total_revenue = sum(order['total'] for order in orders)
            
            completed = len([o for o in orders if o['status'] == 'completed'])
            cancelled = len([o for o in orders if o['status'] == 'cancelled'])
            
            summary = f"📊 Daily Summary - {today}\n\n"
            summary += f"📦 Total Orders: {total_orders}\n"
            summary += f"✅ Completed: {completed}\n"
            summary += f"❌ Cancelled: {cancelled}\n"
            summary += f"💰 Revenue: PKR {total_revenue}\n"
            
            print("\n" + "="*60)
            print(summary)
            print("="*60 + "\n")
            
            # TODO: Send to staff WhatsApp
            
            return True
            
        except Exception as e:
            print(f"Error generating daily summary: {str(e)}")
            return False
    
    
    def _get_order_details(self, order_id: int) -> Optional[Dict]:
        """Get basic order details"""
        try:
            response = self.supabase.table('orders').select('*').eq('id', order_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting order details: {str(e)}")
            return None
    
    
    def _get_order_with_student(self, order_id: int) -> Optional[Dict]:
        """Get order with student information"""
        try:
            response = self.supabase.table('orders').select(
                '*, students(whatsapp_number, name)'
            ).eq('id', order_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting order with student: {str(e)}")
            return None
    
    
    def _get_order_with_items(self, order_id: int) -> Optional[Dict]:
        """Get order with all items"""
        try:
            response = self.supabase.table('orders').select(
                '*, order_items(*, menu_items(*))'
            ).eq('id', order_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting order with items: {str(e)}")
            return None


# Create singleton instance
notification_service = NotificationService()