class Transaction:

    def __init__(self, db):
        self.db = db

    def __enter__(self):
        self.db.__enter__()
        self.cursor = self.db.cursor()
        self.cursor.__enter__()

        return self.cursor

    def __exit__(self, type, value, traceback):
        self.cursor.__exit__(type, value, traceback)
        self.db.__exit__(type, value, traceback)
