"""
Order Management Routes
API endpoints for order operations
UPDATED VERSION WITH NOTIFICATION INTEGRATION
"""
from flask import Blueprint, request, jsonify
from app.utils.supabase_client import supabase_client
from app.services.notification_service import notification_service
from datetime import datetime

order_bp = Blueprint('order', __name__)


@order_bp.route('/', methods=['POST'])
def create_order():
    """
    Create a new order
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['student_id', 'items', 'total']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Create order
        order_data = {
            'student_id': data['student_id'],
            'total': data['total'],
            'status': 'pending',
            'created_at': datetime.utcnow().isoformat()
        }
        
        order_response = supabase_client.table('orders').insert(order_data).execute()
        
        if not order_response.data:
            return jsonify({
                'status': 'error',
                'message': 'Failed to create order'
            }), 500
        
        order_id = order_response.data[0]['id']
        
        # Create order items
        order_items = []
        for item in data['items']:
            order_items.append({
                'order_id': order_id,
                'menu_item_id': item['menu_item_id'],
                'quantity': item['quantity'],
                'subtotal': item['subtotal']
            })
        
        supabase_client.table('order_items').insert(order_items).execute()
        
        # NEW: Notify staff about new order
        notification_service.notify_staff_new_order(order_id)
        
        return jsonify({
            'status': 'success',
            'data': {
                'order_id': order_id,
                'message': 'Order created successfully'
            }
        }), 201
        
    except Exception as e:
        print(f"Error creating order: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@order_bp.route('/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """
    Get order details by ID
    """
    try:
        response = supabase_client.table('orders').select(
            '*, students(id, name, whatsapp_number), order_items(*, menu_items(*))'
        ).eq('id', order_id).execute()
        
        if not response.data:
            return jsonify({
                'status': 'error',
                'message': 'Order not found'
            }), 404
        
        return jsonify({
            'status': 'success',
            'data': response.data[0]
        }), 200
        
    except Exception as e:
        print(f"Error getting order: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@order_bp.route('/<int:order_id>/status', methods=['PATCH'])
def update_order_status(order_id):
    """
    Update order status
    UPDATED: Now sends notifications to customers
    """
    try:
        data = request.get_json()
        
        if 'status' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Status field is required'
            }), 400
        
        new_status = data['status']
        valid_statuses = ['pending', 'confirmed', 'preparing', 'ready', 'completed', 'cancelled']
        
        if new_status not in valid_statuses:
            return jsonify({
                'status': 'error',
                'message': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
            }), 400
        
        # Update order status in database
        response = supabase_client.table('orders').update({
            'status': new_status,
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', order_id).execute()
        
        if not response.data:
            return jsonify({
                'status': 'error',
                'message': 'Order not found'
            }), 404
        
        # NEW: Send notification to customer about status change
        notification_sent = notification_service.notify_order_status_change(order_id, new_status)
        
        return jsonify({
            'status': 'success',
            'data': response.data[0],
            'notification_sent': notification_sent,
            'message': f'Order status updated to {new_status}'
        }), 200
        
    except Exception as e:
        print(f"Error updating order status: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@order_bp.route('/student/<int:student_id>', methods=['GET'])
def get_student_orders(student_id):
    """
    Get all orders for a specific student
    NEW: Added for order history feature
    """
    try:
        # Get query parameters
        limit = request.args.get('limit', 10, type=int)
        status = request.args.get('status', None)
        
        # Build query
        query = supabase_client.table('orders').select(
            '*, order_items(*, menu_items(name, price))'
        ).eq('student_id', student_id)
        
        # Filter by status if provided
        if status:
            query = query.eq('status', status)
        
        # Order by most recent first
        query = query.order('created_at', desc=True).limit(limit)
        
        response = query.execute()
        
        return jsonify({
            'status': 'success',
            'data': response.data,
            'count': len(response.data)
        }), 200
        
    except Exception as e:
        print(f"Error getting student orders: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@order_bp.route('/stats', methods=['GET'])
def get_order_stats():
    """
    Get order statistics
    NEW: Added for analytics
    """
    try:
        # Get date range from query params
        from datetime import datetime, timedelta
        
        today = datetime.utcnow().date()
        start_date = request.args.get('start_date', today.isoformat())
        end_date = request.args.get('end_date', today.isoformat())
        
        # Get orders in date range
        response = supabase_client.table('orders').select(
            'id, total, status, created_at'
        ).gte('created_at', f'{start_date}T00:00:00').lte(
            'created_at', f'{end_date}T23:59:59'
        ).execute()
        
        orders = response.data
        
        # Calculate statistics
        total_orders = len(orders)
        total_revenue = sum(order['total'] for order in orders)
        
        status_breakdown = {}
        for order in orders:
            status = order['status']
            status_breakdown[status] = status_breakdown.get(status, 0) + 1
        
        return jsonify({
            'status': 'success',
            'data': {
                'date_range': {
                    'start': start_date,
                    'end': end_date
                },
                'total_orders': total_orders,
                'total_revenue': float(total_revenue),
                'status_breakdown': status_breakdown,
                'average_order_value': float(total_revenue / total_orders) if total_orders > 0 else 0
            }
        }), 200
        
    except Exception as e:
        print(f"Error getting order stats: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@order_bp.route('/<int:order_id>', methods=['DELETE'])
def cancel_order(order_id):
    """
    Cancel an order (soft delete by updating status)
    NEW: Added cancel functionality with notification
    """
    try:
        # Update order status to cancelled
        response = supabase_client.table('orders').update({
            'status': 'cancelled',
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', order_id).execute()
        
        if not response.data:
            return jsonify({
                'status': 'error',
                'message': 'Order not found'
            }), 404
        
        # Send cancellation notification
        notification_sent = notification_service.notify_order_status_change(order_id, 'cancelled')
        
        return jsonify({
            'status': 'success',
            'message': 'Order cancelled successfully',
            'notification_sent': notification_sent
        }), 200
        
    except Exception as e:
        print(f"Error cancelling order: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@order_bp.route('/recent', methods=['GET'])
def get_recent_orders():
    """
    Get recent orders (last 24 hours)
    NEW: Added for quick access to recent orders
    """
    try:
        from datetime import datetime, timedelta
        
        # Calculate 24 hours ago
        time_24h_ago = (datetime.utcnow() - timedelta(hours=24)).isoformat()
        
        response = supabase_client.table('orders').select(
            '*, students(name, whatsapp_number), order_items(*, menu_items(name))'
        ).gte('created_at', time_24h_ago).order('created_at', desc=True).execute()
        
        return jsonify({
            'status': 'success',
            'data': response.data,
            'count': len(response.data)
        }), 200
        
    except Exception as e:
        print(f"Error getting recent orders: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@order_bp.route('/pending-count', methods=['GET'])
def get_pending_count():
    """
    Get count of pending orders
    NEW: Added for staff dashboard quick stats
    """
    try:
        response = supabase_client.table('orders').select(
            'id', count='exact'
        ).in_('status', ['pending', 'confirmed', 'preparing']).execute()
        
        return jsonify({
            'status': 'success',
            'data': {
                'pending_count': response.count if hasattr(response, 'count') else len(response.data)
            }
        }), 200
        
    except Exception as e:
        print(f"Error getting pending count: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@order_bp.route('/<int:order_id>/items', methods=['GET'])
def get_order_items(order_id):
    """
    Get items for a specific order
    NEW: Added for detailed order view
    """
    try:
        response = supabase_client.table('order_items').select(
            '*, menu_items(name, description, price, category)'
        ).eq('order_id', order_id).execute()
        
        if not response.data:
            return jsonify({
                'status': 'error',
                'message': 'No items found for this order'
            }), 404
        
        return jsonify({
            'status': 'success',
            'data': response.data
        }), 200
        
    except Exception as e:
        print(f"Error getting order items: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@order_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    NEW: Added for monitoring
    """
    return jsonify({
        'status': 'healthy',
        'service': 'Order Management API',
        'version': '2.0.0'
    }), 200