class Order:
    def __init__(self,user_id,payment_id,payment_details):
        self.user_id = user_id
        self.payment_id = payment_id
        self.payment_details = payment_details

    def to_json(self):
        return {"user_id" : self.user_id, "payment_id" : self.payment_id, "payment_details" : self.payment_details}
    