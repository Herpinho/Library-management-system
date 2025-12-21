CREATE TABLE IF NOT EXISTS loans (
    loan_id SERIAL PRIMARY KEY,
    copy_id varchar(50),
    user_id INTEGER NOT NULL,
    loan_date DATE DEFAULT CURRENT_DATE,
    due_date DATE NOT NULL,
    return_date DATE,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'returned', 'overdue'))
);