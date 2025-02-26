from flask import Blueprint, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db, UserCrops

crops_bp = Blueprint('crops', __name__)

@crops_bp.route('/add-crop', methods=['POST'])
@login_required
def add_crop():
    data = request.get_json()
    category = data.get('category')
    crop_name = data.get('crop_name')

    if not category or not crop_name:
        return jsonify({'success': False, 'message': 'Category and Crop Name are required'}), 400

    # Check if the crop already exists for the user
    existing_crop = UserCrops.query.filter_by(user_id=current_user.id, category=category, crop_name=crop_name).first()
    if existing_crop:
        return jsonify({'success': False, 'message': 'Crop already added'}), 400

    # Add new crop
    new_crop = UserCrops(user_id=current_user.id, category=category, crop_name=crop_name)
    db.session.add(new_crop)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Crop added successfully'})


@crops_bp.route('/remove-crop', methods=['POST'])
@login_required
def remove_crop():
    data = request.get_json()
    category = data.get('category')
    crop_name = data.get('crop_name')

    if not category or not crop_name:
        return jsonify({'success': False, 'message': 'Category and Crop Name are required'}), 400

    # Find and delete the crop
    crop_to_remove = UserCrops.query.filter_by(user_id=current_user.id, category=category, crop_name=crop_name).first()
    if not crop_to_remove:
        return jsonify({'success': False, 'message': 'Crop not found'}), 404

    db.session.delete(crop_to_remove)
    db.session.commit()

    
    return jsonify({'success': True, 'message': 'Crop removed successfully'})

@crops_bp.route('/show-crops', methods=['GET'])
@login_required
def show_crops():
    # Query all crops registered by the logged-in user
    user_crops = UserCrops.query.filter_by(user_id=current_user.id).all()
    
    # Convert the results into a list of dictionaries
    crops_list = [{'category': crop.category, 'crop_name': crop.crop_name} for crop in user_crops]

    return jsonify({'success': True, 'crops': crops_list})

