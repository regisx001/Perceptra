from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import func

from src.extensions import db
from src.models.category import Category
from src.models.image import Image

categories_bp = Blueprint("categories", __name__)


def _is_descendant(parent_id: str, potential_child_id: str, user_id: str) -> bool:
    """
    Check if potential_child_id is a descendant of parent_id for the given user.
    """
    current_id = potential_child_id
    visited = set()
    while current_id:
        if current_id in visited:
            break
        visited.add(current_id)

        cat = Category.query.filter_by(id=current_id, user_id=user_id).first()
        if not cat or not cat.parent_id:
            break
        if cat.parent_id == parent_id:
            return True
        current_id = cat.parent_id
    return False


@categories_bp.route("", methods=["POST"])
@jwt_required()
def create_category():
    user_id = str(get_jwt_identity())
    data = request.get_json(silent=True) or {}

    raw_name = data.get("name")
    if raw_name is None or not isinstance(raw_name, str):
        return jsonify({"error": "Name is required and must be a string"}), 400

    name = raw_name.strip()
    if not (1 <= len(name) <= 100):
        return jsonify({"error": "Name must be between 1 and 100 characters"}), 400

    parent_id = data.get("parent_id")
    if parent_id is not None:
        parent_id = str(parent_id).strip()
        if parent_id == "":
            parent_id = None

    if parent_id is not None:
        parent_cat = Category.query.filter_by(id=parent_id, user_id=user_id).first()
        if not parent_cat:
            return jsonify({"error": "Parent category not found"}), 404

    # Check duplicate sibling name for this user under the same parent_id
    existing_sibling = Category.query.filter_by(
        user_id=user_id,
        parent_id=parent_id,
        name=name,
    ).first()
    if existing_sibling:
        return jsonify({"error": "A sibling category with this name already exists"}), 409

    category = Category(
        user_id=user_id,
        parent_id=parent_id,
        name=name,
    )
    db.session.add(category)
    db.session.commit()

    return jsonify({
        "success": True,
        "category": category.to_dict(),
    }), 201


@categories_bp.route("", methods=["GET"])
@jwt_required()
def list_categories():
    user_id = str(get_jwt_identity())
    tree_param = request.args.get("tree", "false").lower() in {"true", "1", "yes"}
    include_counts = request.args.get("include_counts", "false").lower() in {"true", "1", "yes"}

    user_categories = Category.query.filter_by(user_id=user_id).order_by(Category.name.asc()).all()

    counts_map = {}
    if include_counts:
        # Query count of images for each category owned by this user
        counts = (
            db.session.query(Image.category_id, func.count(Image.id))
            .filter(Image.category_id.in_([c.id for c in user_categories]))
            .group_by(Image.category_id)
            .all()
        )
        counts_map = {cat_id: count for cat_id, count in counts}

    if not tree_param:
        cats_data = []
        for cat in user_categories:
            item = cat.to_dict()
            if include_counts:
                item["image_count"] = counts_map.get(cat.id, 0)
            cats_data.append(item)
        return jsonify({
            "success": True,
            "categories": cats_data,
        }), 200

    # Build nested tree
    # 1. Initialize node representation
    nodes = {}
    for cat in user_categories:
        node = {
            "id": cat.id,
            "parent_id": cat.parent_id,
            "name": cat.name,
            "created_at": cat.created_at.isoformat() if cat.created_at else None,
            "children": [],
        }
        if include_counts:
            node["image_count"] = counts_map.get(cat.id, 0)
        nodes[cat.id] = node

    root_nodes = []
    for cat in user_categories:
        node = nodes[cat.id]
        if cat.parent_id and cat.parent_id in nodes:
            nodes[cat.parent_id]["children"].append(node)
        else:
            root_nodes.append(node)

    return jsonify({
        "success": True,
        "categories": root_nodes,
    }), 200


@categories_bp.route("/<category_id>", methods=["GET"])
@jwt_required()
def get_category(category_id: str):
    user_id = str(get_jwt_identity())
    category = Category.query.filter_by(id=category_id, user_id=user_id).first()
    if not category:
        return jsonify({"error": "Category not found"}), 404

    return jsonify({
        "success": True,
        "category": category.to_dict(),
    }), 200


@categories_bp.route("/<category_id>", methods=["PATCH"])
@jwt_required()
def update_category(category_id: str):
    user_id = str(get_jwt_identity())
    category = Category.query.filter_by(id=category_id, user_id=user_id).first()
    if not category:
        return jsonify({"error": "Category not found"}), 404

    data = request.get_json(silent=True) or {}
    new_name = category.name
    new_parent_id = category.parent_id

    # Validate name if provided
    if "name" in data:
        raw_name = data["name"]
        if raw_name is None or not isinstance(raw_name, str):
            return jsonify({"error": "Name must be a string"}), 400
        trimmed_name = raw_name.strip()
        if not (1 <= len(trimmed_name) <= 100):
            return jsonify({"error": "Name must be between 1 and 100 characters"}), 400
        new_name = trimmed_name

    # Validate parent_id if provided
    if "parent_id" in data:
        incoming_parent = data["parent_id"]
        if incoming_parent is not None:
            incoming_parent = str(incoming_parent).strip()
            if incoming_parent == "":
                incoming_parent = None

        if incoming_parent is not None:
            # Cannot be self
            if incoming_parent == category_id:
                return jsonify({"error": "Category cannot be its own parent"}), 400

            # Verify parent exists and belongs to user
            parent_cat = Category.query.filter_by(id=incoming_parent, user_id=user_id).first()
            if not parent_cat:
                return jsonify({"error": "Parent category not found"}), 404

            # Verify incoming_parent is not a descendant of category_id (prevent cycle)
            if _is_descendant(parent_id=category_id, potential_child_id=incoming_parent, user_id=user_id):
                return jsonify({"error": "Cannot move category into its own descendant"}), 400

        new_parent_id = incoming_parent

    # Check sibling name conflict if either name or parent_id changes
    if new_name != category.name or new_parent_id != category.parent_id:
        existing_sibling = (
            Category.query.filter(
                Category.user_id == user_id,
                Category.parent_id == new_parent_id,
                Category.name == new_name,
                Category.id != category_id,
            ).first()
        )
        if existing_sibling:
            return jsonify({"error": "A sibling category with this name already exists"}), 409

    category.name = new_name
    category.parent_id = new_parent_id
    db.session.commit()

    return jsonify({
        "success": True,
        "category": category.to_dict(),
    }), 200


@categories_bp.route("/<category_id>", methods=["DELETE"])
@jwt_required()
def delete_category(category_id: str):
    user_id = str(get_jwt_identity())
    category = Category.query.filter_by(id=category_id, user_id=user_id).first()
    if not category:
        return jsonify({"error": "Category not found"}), 404

    # Promote direct child subcategories to root (parent_id = NULL)
    Category.query.filter_by(parent_id=category.id).update({"parent_id": None})

    # Decouple images assigned to this category (category_id = NULL)
    Image.query.filter_by(category_id=category.id).update({"category_id": None})

    db.session.delete(category)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Category deleted",
    }), 200
