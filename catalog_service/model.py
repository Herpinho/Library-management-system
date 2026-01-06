class Book:
    def __init__(self, book_id, title, author, isbn, genre, publication_year, total_count, available_count):
        self.id = book_id
        self.title = title
        self.author = author
        self.isbn = isbn
        self.genre = genre
        self.publication_year = publication_year
        self.total_count = total_count
        self.available_count = available_count

    def to_json(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "genre": self.genre,
            "publication_year": self.publication_year,
            "total_copies": self.total_count,
            "available_copies": self.available_count
        }
    
class BookCopy:
    def __init__(self, copy_id, book_id, status,rent_price):
        self.copy_id = copy_id
        self.book_id = book_id
        self.status = status
        self.rent_price = rent_price

    def to_json(self):
        return {
            "display_id": f"{self.book_id}.{self.copy_id}", 
            "status": self.status,
            "rent price" : self.rent_price
        }