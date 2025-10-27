from flask import Blueprint, request, jsonify
from model import payment
import requests

payment_blueprint = Blueprint("payment", __name__)

payment = {}

def do_payment(user_id):
    return
def verify_payment(user_id):
    return
@payment_blueprint.route("/<int:payment_id>", methods= ["GET"])
def get_payment(payment_id):
    payment = payment.get(payment_id)
    if payment:
        return jsonify(payment.to_json())
    return jsonify({"error" : "Payment not found"}), 404

@payment_blueprint.route("/", methods=["POST"])
def create_payment():
    payment_data = request.json
    user_id = payment_data["user_id"]

    if not verify_payment(user_id):
        return jsonify({"error" : "User does not exist"}), 404  

    payment = payment(payment_id=payment_data["payment_id"], user_id=user_id, payment_details=payment_data["payment_details"])
    payment[payment.payment_id] = payment
    return jsonify(payment.to_json()), 201