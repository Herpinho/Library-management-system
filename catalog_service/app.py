import psycopg2
from flask import Flask, request, jsonify
from model import Book
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))
from shared_utils import *

app = Flask(__name__)
@app.route('/books', methods=['GET']) #GET WHOLE CATALOG
def get_all_books():
    link = get_db_connection(Path(__file__).parent.name.replace("_service", ""))
    cursor = link.cursor()
    cursor.execute(
        """
            SELECT
                b.book_id,
                b.title,
                b.author,
                b.isbn,
                COUNT(c.copy_id) as total_copies,
                SUM(CASE WHEN c.status = 'available' THEN 1 ELSE 0 END) as available_copies
            FROM books b
            LEFT JOIN book_copies c ON b.book_id = c.book_id
            GROUP BY b.book_id
        """
        )
    rows = cursor.fetchall()

    books = []
    for row in rows:
        book_obj = Book(row[0],row[1],row[2],row[3],row[4],row[5])
        books.append(book_obj.to_json())
    cursor.close()
    link.close()
    return jsonify(books)
@app.route('/books', methods = ['POST']) #ADD A BOOK
def add_book ():
    if check := admin_check(user_id=request.headers.get('User-ID'),password_hash=request.headers.get('Password_Hash')): return check    ##ADMIN COMMAND
    data = request.json
    link = get_db_connection(Path(__file__).parent.name.replace("_service", ""))
    cursor = link.cursor()

    try:
        cursor.execute(
            'INSERT INTO books (title,author,isbn) VALUES (%s, %s, %s) RETURNING book_id',
            (data['title'],data['author'], data['isbn'])
        )
        new_id = cursor.fetchone()[0]
        link.commit()
        return jsonify({"message":"Book created","id":new_id}),201
    except Exception as e:
        return jsonify({"error":str(e)}),500
    finally:
        cursor.close()
        link.close()
@app.route('/books/<int:book_id>/copy', methods =['POST']) #ADD A COPY
def add_copy(book_id):
    if check := admin_check(user_id=request.headers.get('User-ID'),password_hash=request.headers.get('Password_Hash')): return check
    link = get_db_connection(Path(__file__).parent.name.replace("_service", ""))
    cursor = link.cursor()

    cursor.execute(
        'INSERT INTO book_copies (book_id, status) VALUES (%s, %s) RETURNING copy_id',
        (book_id,'available')
    )
    copy_id = cursor.fetchone()[0]
    link.commit()
    cursor.close()
    link.close()

    return jsonify ({"message":"Copy successfully created","copy_id": copy_id}),201
@app.route('/books/<int:book_id>/copy',methods = ['DELETE']) #REMOVE A COPY
def remove_copy(copy_id):
    if check := admin_check(user_id=request.headers.get('User-ID'),password_hash=request.headers.get('Password_Hash')): return check
    link = get_db_connection(Path(__file__).parent.name.replace("_service", ""))
    cursor = link.cursor()
    try:
        cursor.execute('SELECT copy_id FROM book_copies WHERE copy_id = %s', (copy_id,))
        if cursor.fetchone() is None:
            return jsonify ({"error": "Copy_id not found."}),404
        cursor.execute('DELETE FROM book_copies WHERE copy_id = %s', (copy_id,))
        link.commit()
        return jsonify({"message": f"Copy {copy_id} successfully removed."}),200
    except Exception as e:
        link.rollback()
        return jsonify({"error":str(e)}),500
    finally:
        cursor.close()
        link.close()
@app.route('/books/<int:book_id>/copy/<int:copy_id>', methods = ['PUT']) #UPDATE COPY AVAILABILITY
def change_availability(book_id,copy_id):

    if check := admin_check(user_id=request.headers.get('User-ID'),password_hash=request.headers.get('Password_Hash')): return check
    data = request.json
    new_status = data.get('status', 'available')
    link = get_db_connection(Path(__file__).parent.name.replace("_service",""))
    cursor = link.cursor()
    try:
        cursor.execute('SELECT copy_id FROM book_copies WHERE copy_id = %s', (copy_id,))
        if cursor.fetchone() is None:
            return jsonify({"error": "Copy id not found."}),404
        cursor.execute('UPDATE book_copies SET status = %s WHERE copy_id = %s',
                       (new_status, copy_id))
        link.commit()
        return jsonify({"message":f"Copy {copy_id} updated to {new_status}."}),200
    except Exception as e:
        return jsonify({"error":str(e)}),500
    finally:
        cursor.close()
        link.close()

if __name__ == '__main__':
    
    app.run(debug=True, port = 5002)