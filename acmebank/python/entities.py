# Class definitions for the entities

class Customer:
    # Constructor
    def __init__(self, item):
        self.id = item.get('id').get('S')

    # String representation of the object
    def __repr__(self):
        return "User<{} -- >".format(self.id)

class Account:
        # Constructor
    def __init__(self, item):
        self.id = item.get('id').get('S')

    # String representation of the object
    def __repr__(self):
        return "User<{} -- >".format(self.id)

class Transaction:
        # Constructor
    def __init__(self, item):
        self.id = item.get('id').get('S')

    # String representation of the object
    def __repr__(self):
        return "User<{} -- >".format(self.id)
