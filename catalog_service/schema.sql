CREATE TABLE IF NOT EXISTS public.books (
    book_id SERIAL PRIMARY KEY, 
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    isbn VARCHAR(20) UNIQUE,
    available BOOLEAN DEFAULT true
);

CREATE TABLE IF NOT EXISTS public.book_copies (
    copy_id VARCHAR(50) PRIMARY KEY, 
    book_id INTEGER REFERENCES public.books(book_id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'available',
    rent_price DECIMAL(10,2) NOT NULL,
);