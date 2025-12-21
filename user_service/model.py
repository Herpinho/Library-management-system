class User:
    def __init__(self,id,name,email,password,role,creation):
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.role = role
        self.creation = creation


    def to_json(self):
        return {"id" : self.id,
                "name" : self.name,
                "email" : self.email,
                "role" : self.role,
                "creation" : str(self.creation)}
