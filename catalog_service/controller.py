from flask import Blueprint, request, jsonify
from model import Book

catalog_blueprint = Blueprint("Catalog", __name__)

books = {}

@catalog_blueprint.route('/<int:user_id>', methods = ['GET'])

def get_book(book_id):
    book = books.get(book_id)
    if book:
        return jsonify(book.to_json())
    return jsonify({"error: Book not found"}),404

@catalog_blueprint.route('/',methods = ['POST'])
def create_user():
    book_data = request.json
    book = Book(
        book_id = book_data['book_id'],
        book_name = book_data['book_name'],
        book_author = book_data['book_author'],
        book_ammount = book_data['book_ammount'],
        book_availability = book_data['book_availability'],
        book_metadata = book_data["book_metadata"])

