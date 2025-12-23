
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

@app.route('/books/<int:book_id>', methods=['GET'])
def get_book_json(book_id):
    try:
        book_obj = get_book(book_id)
        if book_obj:
            return jsonify(book_obj.to_json()), 200
        return jsonify({"error": f"book {book_id} not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
def get_book(book_id):
    link = get_db_connection(Path(__file__).parent.name.replace("_service", ""))
    cursor = link.cursor()
    try:
        cursor.execute(
            """
                SELECT
                    b.book_id,
                    b.title,
                    b.author,
                    b.isbn,
                    COUNT(c.copy_id) as total_copies,
                    COALESCE(SUM(CASE WHEN c.status = 'available' THEN 1 ELSE 0 END), 0) as available_copies
                FROM public.books b                         
                LEFT JOIN public.book_copies c               
                    ON b.book_id = c.book_id
                WHERE b.book_id = %s
                GROUP BY b.book_id                            
            """, (book_id,)
        )
        row = cursor.fetchone()
        if not row or row[0] is None:
            return None
        return Book(row[0],row[1],row[2],row[3],row[4],row[5])

    except Exception as e:
        print(f"Database error: {e}")
        raise e 
    finally:
        cursor.close()
        link.close()
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
@app.route('/<int:book_id>/copy/', methods =['POST']) #ADD A COPY
def add_copy(book_id):
    if check := admin_check(user_id=request.headers.get('User-ID'),password_hash=request.headers.get('Password_Hash')): return check
    link = get_db_connection(Path(__file__).parent.name.replace("_service", ""))
    cursor = link.cursor()
    try:
        cursor.execute('SELECT COUNT(*) FROM book_copies WHERE book_id = %s', (book_id,))
        data = request.json
        rent_price = data['rent_price']
        count = cursor.fetchone()[0]
        new_copy_id = f"{book_id}.{count+1}"
        cursor.execute(
            'INSERT INTO book_copies (book_id,copy_id, status,rent_price) VALUES (%s, %s, %s,%s) RETURNING copy_id',
            (book_id,new_copy_id,'available',rent_price,)
        )
        copy_id = cursor.fetchone()[0]
        link.commit()
        return jsonify ({"message":"Copy successfully created","copy_id": copy_id}),201
    except Exception as e:
        return jsonify({"error":str(e)}),500
    finally:
        cursor.close()
        link.close()
@app.route('/copy/<int:copy_id>',methods = ['DELETE']) #REMOVE A COPY
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
@app.route('/copy/', methods = ['PUT']) #UPDATE COPY AVAILABILITY
def change_availability():
    if check := admin_check(user_id=request.headers.get('User-ID'),password_hash=request.headers.get('Password_Hash')): return check
    data = request.json
    status = data['status']
    copy_id = data['copy_id']
    if not status:
        new_status = data.get('status', 'available')
    else: new_status = status

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
@app.route('/copy/', methods = ['GET'])
def get_copy():
    link = get_db_connection(Path(__file__).parent.name.replace("_service",""))
    cursor = link.cursor()
    data = request.json
    copy_id = data['copy_id']
    try:
        cursor.execute('SELECT status,rent_price FROM book_copies WHERE copy_id = %s',(copy_id,))
        copy = cursor.fetchone()
        if not copy:
            return jsonify({"error":'copy id not found.'}),404
        return jsonify(copy)
    except Exception as e:
        return jsonify({"error":str(e)}),500
    finally:
        cursor.close()
        link.close()        
        
if __name__ == '__main__':
    
    app.run(debug=True, port = 5002)