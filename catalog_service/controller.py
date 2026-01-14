from flask import Blueprint, request, jsonify
from pathlib import Path
from model import Book,BookCopy
from shared_utils.utils import *

book_blueprint = Blueprint('book_blueprint', __name__)

import requests


@book_blueprint.route('/import', methods=['POST'])
def import_book_from_api():

    
    data = request.json
    search_query = data.get('query')  
    
    if not search_query:
        return jsonify({"error": "Search query is required"}), 400
    
    try:
        api_url = f"https://www.googleapis.com/books/v1/volumes?q={search_query}"
        response = requests.get(api_url)
        
        if response.status_code != 200:
            return jsonify({"error": "Failed to connect to Google Books API"}), 500
        
        api_data = response.json()
        
        if 'items' not in api_data or len(api_data['items']) == 0:
            return jsonify({"error": "No books found with that search term"}), 404
        
        book_info = api_data['items'][0]['volumeInfo']
        
        title = book_info.get('title', 'Unknown Title')
        authors = book_info.get('authors', ['Unknown Author'])
        author = ', '.join(authors)  
        
        isbn = None
        if 'industryIdentifiers' in book_info:
            for identifier in book_info['industryIdentifiers']:
                if identifier['type'] in ['ISBN_13', 'ISBN_10']:
                    isbn = identifier['identifier']
                    break
        
        categories = book_info.get('categories', [])
        genre = categories[0] if categories else None
        
        published_date = book_info.get('publishedDate', '')
        publication_year = None
        if published_date:
            try:
                publication_year = int(published_date.split('-')[0])  
            except:
                publication_year = None
        
        link = get_db_connection()
        cursor = link.cursor()
        
        try:
            cursor.execute(
                'INSERT INTO books (title, author, isbn, genre, publication_year) VALUES (%s, %s, %s, %s, %s) RETURNING book_id',
                (title, author, isbn, genre, publication_year)
            )
            new_id = cursor.fetchone()[0]
            link.commit()
            
            return jsonify({
                "message": "Book imported successfully",
                "id": new_id,
                "book": {
                    "title": title,
                    "author": author,
                    "isbn": isbn,
                    "genre": genre,
                    "publication_year": publication_year
                }
            }), 201
        except Exception as e:
            link.rollback()
            return jsonify({"error": f"Database error: {str(e)}"}), 500
        finally:
            cursor.close()
            link.close()
            
    except Exception as e:
        return jsonify({"error": f"API error: {str(e)}"}), 500

def get_book_obj(book_id):
    link = get_db_connection()
    cursor = link.cursor()
    try:
        cursor.execute(
            """
                SELECT
                    b.book_id,
                    b.title,
                    b.author,
                    b.genre,
                    b.publication_year,
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
        return Book(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
    except Exception as e:
        print(f"Database error: {e}")
        raise e 
    finally:
        cursor.close()
        link.close()

@book_blueprint.route('/', methods=['GET'])
def get_all_books():
    link = get_db_connection()
    cursor = link.cursor()
    cursor.execute(
        """
            SELECT
                b.book_id,
                b.title,
                b.author,
                b.genre,
                b.publication_year,
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
        book_obj = Book(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
        books.append(book_obj.to_json())
    cursor.close()
    link.close()
    return jsonify(books)


@book_blueprint.route('/search', methods=['GET'])
def search_books():
    title = request.args.get('title')
    author = request.args.get('author')
    genre = request.args.get('genre')
    
    link = get_db_connection()
    cursor = link.cursor()
    
    try:
        if title:
            cursor.execute(
                """
                    SELECT
                        b.book_id, b.title, b.author, b.genre, b.publication_year,
                        COUNT(c.copy_id) as total_copies,
                        SUM(CASE WHEN c.status = 'available' THEN 1 ELSE 0 END) as available_copies
                    FROM books b
                    LEFT JOIN book_copies c ON b.book_id = c.book_id
                    WHERE LOWER(b.title) LIKE LOWER(%s)
                    GROUP BY b.book_id
                """,
                (f'%{title}%',)
            )
        elif author:
            cursor.execute(
                """
                    SELECT
                        b.book_id, b.title, b.author, b.genre, b.publication_year,
                        COUNT(c.copy_id) as total_copies,
                        SUM(CASE WHEN c.status = 'available' THEN 1 ELSE 0 END) as available_copies
                    FROM books b
                    LEFT JOIN book_copies c ON b.book_id = c.book_id
                    WHERE LOWER(b.author) LIKE LOWER(%s)
                    GROUP BY b.book_id
                """,
                (f'%{author}%',)
            )
        elif genre:
            cursor.execute(
                """
                    SELECT
                        b.book_id, b.title, b.author, b.genre, b.publication_year,
                        COUNT(c.copy_id) as total_copies,
                        SUM(CASE WHEN c.status = 'available' THEN 1 ELSE 0 END) as available_copies
                    FROM books b
                    LEFT JOIN book_copies c ON b.book_id = c.book_id
                    WHERE b.genre = %s
                    GROUP BY b.book_id
                """,
                (genre,)
            )
        else:
            return jsonify({"error": "Please provide title, author, or genre parameter"}), 400
        
        rows = cursor.fetchall()
        books = []
        for row in rows:
            book_obj = Book(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
            books.append(book_obj.to_json())
        
        return jsonify(books), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        link.close()

@book_blueprint.route('/search_google', methods=['POST'])
def search_google_books():

    
    data = request.json
    search_query = data.get('query')
    search_type = data.get('type', 'title')
    language = data.get('language', 'en')
    
    if not search_query:
        return jsonify({"error": "Search query is required"}), 400
    
    try:
        lang_param = f"lang_{language}"
        
        if search_type == 'author':
            api_url = f"https://www.googleapis.com/books/v1/volumes?q=inauthor:{search_query}&langRestrict={language}&lr={lang_param}&maxResults=10"
        else:
            api_url = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{search_query}&langRestrict={language}&lr={lang_param}&maxResults=10"
        
        print(f"API URL: {api_url}")
        
        response = requests.get(api_url)
        
        if response.status_code != 200:
            return jsonify({"error": "Failed to connect to Google Books API"}), 500
        
        api_data = response.json()
        
        if 'items' not in api_data or len(api_data['items']) == 0:
            return jsonify({"error": "No books found with that search term"}), 404
        
        results = []
        for idx, item in enumerate(api_data['items']):
            if len(results) >= 5:
                break
                
            book_info = item['volumeInfo']
            
            book_language = book_info.get('language', 'unknown')
            if language == 'en' and book_language not in ['en', 'en-US', 'en-GB']:
                continue
            if language == 'pt' and book_language not in ['pt', 'pt-BR', 'pt-PT']:
                continue
            
            title = book_info.get('title', 'Unknown Title')
            authors = book_info.get('authors', ['Unknown Author'])
            author = ', '.join(authors)
            
            isbn = None
            if 'industryIdentifiers' in book_info:
                for identifier in book_info['industryIdentifiers']:
                    if identifier['type'] in ['ISBN_13', 'ISBN_10']:
                        isbn = identifier['identifier']
                        break
            
            categories = book_info.get('categories', [])
            genre = categories[0] if categories else None
            
            published_date = book_info.get('publishedDate', '')
            publication_year = None
            if published_date:
                try:
                    publication_year = int(published_date.split('-')[0])
                except:
                    publication_year = None
            
            results.append({
                "index": len(results) + 1,
                "title": title,
                "author": author,
                "isbn": isbn,
                "genre": genre,
                "publication_year": publication_year,
                "language": book_language
            })
        
        if not results:
            return jsonify({"error": f"No books found in {language.upper()}"}), 404
        
        return jsonify({"results": results}), 200
            
    except Exception as e:
        return jsonify({"error": f"API error: {str(e)}"}), 500

@book_blueprint.route('/import_selected', methods=['POST'])
def import_selected_book():

    
    data = request.json
    title = data.get('title')
    author = data.get('author')
    genre = data.get('genre')
    publication_year = data.get('publication_year')
    
    if not title or not author:
        return jsonify({"error": "Title and author are required"}), 400
    
    link = get_db_connection()
    cursor = link.cursor()
    
    try:
        cursor.execute(
            'INSERT INTO books (title, author, genre, publication_year) VALUES (%s, %s, %s, %s) RETURNING book_id',
            (title, author, genre, publication_year)
        )
        new_id = cursor.fetchone()[0]
        link.commit()
        
        return jsonify({
            "message": "Book imported successfully",
            "id": new_id,
            "book": {
                "title": title,
                "author": author,
                "genre": genre,
                "publication_year": publication_year
            }
        }), 201
    except Exception as e:
        link.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()
        link.close()

@book_blueprint.route('/<int:book_id>/search_editions', methods=['GET'])
def search_editions(book_id):

    
    book_obj = get_book_obj(book_id)
    if not book_obj:
        return jsonify({"error": "Book not found"}), 404
    
    try:
        query = f"{book_obj.title} {book_obj.author}"
        api_url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=15"
        
        response = requests.get(api_url)
        
        if response.status_code != 200:
            return jsonify({"error": "Failed to connect to Google Books API"}), 500
        
        api_data = response.json()
        
        if 'items' not in api_data or len(api_data['items']) == 0:
            return jsonify({"error": "No editions found"}), 404
        
        editions = []
        for idx, item in enumerate(api_data['items']):
            if len(editions) >= 5:
                break
                
            book_info = item['volumeInfo']
            
            isbn = None
            isbn_type = None
            if 'industryIdentifiers' in book_info:
                for identifier in book_info['industryIdentifiers']:
                    if identifier['type'] in ['ISBN_13', 'ISBN_10']:
                        isbn = identifier['identifier']
                        isbn_type = identifier['type']
                        break
            
            if not isbn:
                continue
            
            edition_title = book_info.get('title', '')
            publisher = book_info.get('publisher', 'Unknown Publisher')
            published_date = book_info.get('publishedDate', 'Unknown')
            
            edition_info = f"{publisher}, {published_date}"
            
            editions.append({
                "index": len(editions) + 1,
                "isbn": isbn,
                "isbn_type": isbn_type,
                "edition_info": edition_info,
                "full_title": edition_title,
                "publisher": publisher,
                "published_date": published_date
            })
        
        if not editions:
            return jsonify({"error": "No editions with ISBN found"}), 404
        
        return jsonify({"editions": editions}), 200
            
    except Exception as e:
        return jsonify({"error": f"API error: {str(e)}"}), 500

@book_blueprint.route('/genres', methods=['GET'])
def get_genres():
    link = get_db_connection()
    cursor = link.cursor()
    try:
        cursor.execute(
            """
                SELECT DISTINCT genre 
                FROM books 
                WHERE genre IS NOT NULL 
                ORDER BY genre
            """
        )
        rows = cursor.fetchall()
        genres = [row[0] for row in rows]
        return jsonify(genres), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        link.close()

@book_blueprint.route('/<int:book_id>', methods=['GET'])
def get_book_json(book_id):
    try:
        book_obj = get_book_obj(book_id)
        if book_obj:
            return jsonify(book_obj.to_json()), 200
        return jsonify({"error": f"book {book_id} not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@book_blueprint.route('/', methods = ['POST'])
def add_book():

    data = request.json
    link = get_db_connection()
    cursor = link.cursor()
    try:
        cursor.execute(
            'INSERT INTO books (title, author, genre, publication_year) VALUES (%s, %s, %s, %s) RETURNING book_id',
            (data['title'], data['author'], data.get('genre'), data.get('publication_year'))
        )
        new_id = cursor.fetchone()[0]
        link.commit()
        return jsonify({"message": "Book created", "id": new_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        link.close()

@book_blueprint.route('/<int:book_id>/copy/', methods =['POST'])
def add_copy(book_id):

    link = get_db_connection()
    cursor = link.cursor()
    try:
        cursor.execute('SELECT COUNT(*) FROM book_copies WHERE book_id = %s', (book_id,))
        data = request.json
        rent_price = data['rent_price']
        isbn = data.get('isbn')
        edition_info = data.get('edition_info', '')
        
        count = cursor.fetchone()[0]
        new_copy_id = f"{book_id}.{count+1}"
        
        cursor.execute(
            'INSERT INTO book_copies (book_id, copy_id, isbn, edition_info, status, rent_price) VALUES (%s, %s, %s, %s, %s, %s) RETURNING copy_id',
            (book_id, new_copy_id, isbn, edition_info, 'available', rent_price)
        )
        copy_id = cursor.fetchone()[0]
        link.commit()
        return jsonify({"message": "Copy successfully created", "copy_id": copy_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        link.close()


@book_blueprint.route('/copy/<string:copy_id>',methods = ['DELETE'])
def remove_copy(copy_id):
    if check := admin_check(user_id=request.headers.get('User-ID'),password_hash=request.headers.get('Password_Hash')): return check
    link = get_db_connection()
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

@book_blueprint.route('/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):

    link = get_db_connection()
    cursor = link.cursor()
    try:
        cursor.execute('SELECT book_id FROM books WHERE book_id = %s', (book_id,))
        if cursor.fetchone() is None:
            return jsonify({"error": "book_id not found."}), 404
        
        cursor.execute('DELETE FROM books WHERE book_id = %s', (book_id,))
        link.commit()
        return jsonify({"message": f"Book {book_id} and all its copies successfully removed"}), 200
    except Exception as e:
        link.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        link.close()

@book_blueprint.route('/copy/', methods = ['PUT'])
def change_availability():
    data = request.json
    status = data.get('status')
    copy_id = data.get('copy_id')
    new_status = status if status else data.get('status', 'available')
    link = get_db_connection()
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

@book_blueprint.route('/copy/', methods = ['GET'])
def get_copy():
    link = get_db_connection()
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

@book_blueprint.route('/<int:book_id>/available_copies', methods=['GET'])
def get_available_copies(book_id):
    link = get_db_connection()
    cursor = link.cursor()
    try:
        cursor.execute(
            """
                SELECT copy_id, isbn, edition_info, rent_price
                FROM book_copies
                WHERE book_id = %s AND status = 'available'
                ORDER BY copy_id
            """, (book_id,)
        )
        rows = cursor.fetchall()
        
        if not rows:
            return jsonify({"message": "No available copies"}), 404
        
        copies = []
        for row in rows:
            copies.append({
                "copy_id": row[0],
                "isbn": row[1] if row[1] else "N/A",
                "edition_info": row[2] if row[2] else "Standard Edition",
                "rent_price": float(row[3])
            })
        
        return jsonify({"copies": copies}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        link.close()

@book_blueprint.route('/<int:book_id>/copies', methods=['GET'])
def get_book_copies(book_id): 
    link = get_db_connection()
    cursor = link.cursor()
    try:
        cursor.execute(
            """
                SELECT copy_id, isbn, edition_info, status, rent_price
                FROM book_copies
                WHERE book_id = %s
                ORDER BY copy_id
            """, (book_id,)
        )
        rows = cursor.fetchall()
        
        if not rows:
            return jsonify({"message": "No copies found"}), 404
        
        copies = []
        copies = [BookCopy(row[0],row[1],row[2],row[3],row[4]).to_json() for row in rows]
        return jsonify(copies), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        link.close()