class Payment:
    def __init__(self,payment_id,user_id,loan_id,amount,status,transaction_id):
        self.payment_id = payment_id 
        self.user_id = user_id
        self.loan_id = loan_id
        self.amount = amount
        self.status = status #pending,completed,cancelled,failed
        self.transaction_id = transaction_id 

    def to_json(self):
        return {
            "payment_id" : self.payment_id,
            "user_id" : self.user_id,
            "loan_id" : self.loan_id,
            "amount" : float(self.amount),
            "status" : self.status,
            "transaction_id" : self.transaction_id
            }
    