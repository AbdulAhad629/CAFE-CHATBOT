"""
Menu Management Routes
API endpoints for menu operations
"""
from flask import Blueprint, request, jsonify
from app.utils.supabase_client import supabase_client

menu_bp = Blueprint('menu', __name__)

@menu_bp.route('/', methods=['GET'])
def get_menu():
    """
    Get all available menu items
    """
    try:
        response = supabase_client.table('menu_items').select('*').eq('available', True).execute()
        return jsonify({
            'status': 'success',
            'data': response.data
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@menu_bp.route('/<int:item_id>', methods=['GET'])
def get_menu_item(item_id):
    """
    Get specific menu item by ID
    """
    try:
        response = supabase_client.table('menu_items').select('*').eq('id', item_id).execute()
        
        if not response.data:
            return jsonify({
                'status': 'error',
                'message': 'Menu item not found'
            }), 404
        
        return jsonify({
            'status': 'success',
            'data': response.data[0]
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@menu_bp.route('/category/<category>', methods=['GET'])
def get_menu_by_category(category):
    """
    Get menu items by category
    """
    try:
        response = supabase_client.table('menu_items').select('*').eq('category', category).eq('available', True).execute()
        
        return jsonify({
            'status': 'success',
            'data': response.data
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
