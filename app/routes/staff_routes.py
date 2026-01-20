"""
Staff Dashboard Routes
Web interface for cafe staff to manage orders
"""
from flask import Blueprint, render_template, jsonify
from app.utils.supabase_client import supabase_client

staff_bp = Blueprint('staff', __name__)

@staff_bp.route('/dashboard')
def dashboard():
    """
    Staff dashboard main page
    """
    return render_template('staff/dashboard.html')


@staff_bp.route('/orders/pending', methods=['GET'])
def get_pending_orders():
    """
    Get all pending orders
    """
    try:
        response = supabase_client.table('orders').select(
            '*, students(name, whatsapp_number), order_items(*, menu_items(name, price))'
        ).in_('status', ['pending', 'confirmed', 'preparing']).order('created_at').execute()
        
        return jsonify({
            'status': 'success',
            'data': response.data
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@staff_bp.route('/orders/history', methods=['GET'])
def get_order_history():
    """
    Get completed orders history
    """
    try:
        response = supabase_client.table('orders').select(
            '*, students(name), order_items(*, menu_items(name))'
        ).in_('status', ['completed', 'cancelled']).order('created_at', desc=True).limit(50).execute()
        
        return jsonify({
            'status': 'success',
            'data': response.data
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@staff_bp.route('/reports/sales', methods=['GET'])
def get_sales_report():
    """
    Get sales report
    """
    try:
        # Get completed orders with their totals
        response = supabase_client.table('orders').select(
            'id, total, created_at, order_items(quantity, menu_items(name, category))'
        ).eq('status', 'completed').execute()
        
        # TODO: Process data for meaningful reports
        # - Daily/Weekly/Monthly totals
        # - Popular items
        # - Peak hours
        
        return jsonify({
            'status': 'success',
            'data': response.data
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
