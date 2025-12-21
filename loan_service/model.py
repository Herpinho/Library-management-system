class Loan:
    def __init__(self,loan_id,book_id,user_id,loan_date,due_date,return_date=None, status='active'):
        self.loan_id = loan_id
        self.book_id = book_id
        self.user_id = user_id
        self.loan_date = loan_date
        self.due_date = due_date
        self.return_date = return_date
        self.status = status # active, overdue, returned
    def to_json(self):
        return {
            "loan_id" : self.loan_id,
            "book_id" : self.book_id,
            "user_id" : self.user_id,
            "loan_date" : self.loan_date,
            "due_date" : self.due_date,
            "return_date" : self.return_date,
            "status" : self.status,
            "overdue" : (self.status == 'overdue')
        }