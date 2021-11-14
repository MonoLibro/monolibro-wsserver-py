class User:
    def __init__(self, username):
        self.username = username
        self.clients = []

    def join(self, client):
        self.clients.append(client)

    def leave(self, client):
        self.pop(self.clients.index(client))

    def is_empty(self):
        return len(self.clients) == 0
