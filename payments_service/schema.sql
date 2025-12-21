CREATE TABLE IF NOT EXISTS payments (
	payment_id SERIAL PRIMARY KEY,
	user_id INT NOT NULL,
	loan_id INT NOT NULL,
	amount DECIMAL(10,2) NOT NULL,
	payment_status VARCHAR(20) DEFAULT 'pending',
	transaction_id VARCHAR(100)
);