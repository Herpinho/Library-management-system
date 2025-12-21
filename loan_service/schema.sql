CREATE TABLE IF NOT EXISTS loans (
    loan_id SERIAL PRIMARY KEY,
    copy_id INTEGER NOT NULL,  -- Links to a specific book copy
    user_id INTEGER NOT NULL,  -- Links to the user from User Service
    loan_date DATE DEFAULT CURRENT_DATE,
    due_date DATE NOT NULL,
    return_date DATE,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'returned', 'overdue'))
);