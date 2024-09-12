from models import get_scoped_session, User


class BlackjackPlayer:

    def __init__(self, id):
        self.id = id
        self.name = ''
        self.balance = 0
        self.sid = ''
        self.game_id = ''


    def update(self):
        if self.id:
            session = get_scoped_session()
            user = session.get(User, self.id)
            self.name = user.name
            self.balance = user.balance
            self.sid = user.sid
            self.game_id = user.game_id

    def can_bet(self, amount):
        self.update()
        return self.balance >= amount

    def add_funds(self, amount):
        session = get_scoped_session()
        try:
            user = session.get(User, self.id)
            user.balance += amount
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error adding funds: {e}")

    def remove_funds(self, amount):
        session = get_scoped_session()
        try:
            if self.can_bet(amount):
                user = session.get(User, self.id)
                user.balance -= amount
                session.commit()
            else:
                print(f"Player {self.id} cannot bet {amount}.")
        except Exception as e:
            session.rollback()
            print(f"Error removing funds: {e}")


    @property
    def state(self):
        self.update()
        return {
            'id': self.id,
            'name': self.name,
            'balance': self.balance,
        }
