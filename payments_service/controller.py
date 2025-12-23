from flask import Blueprint, request, jsonify
from model import Payment
import requests

payment_blueprint = Blueprint("payment", __name__)

payment = {}

