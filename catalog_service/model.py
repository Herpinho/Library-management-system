class Book:
    def __init__(self,book_id,book_name,book_author,book_ammount,book_availability,book_metadata):
        self.book_id = book_id
        self.book_name = book_name
        self.book_author = book_author
        self.book_ammount = book_ammount
        self.book_availability = book_availability
        self.book_metadata = book_metadata
    def to_json(self):
        return {"book_id": self.book_id,
                "book_name": self.book_name,
                "book_author": self.book_author,
                "book_ammount": self.book_ammount,
                "book_availability": self.book_availability,
                "book_metadata": self.book_metadata}
