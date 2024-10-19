from typing import Optional
from database.database import get_session
from sqlmodel import SQLModel, Field



class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True)
    password: str
    balance: int = Field(default=100)

    def check_password(self, password: str) -> bool:
        return self._password == password

    def add_balance(self, amount: int) -> None:
        self.balance += amount

    def subtract_balance(self, amount: int) -> bool:
        if self.balance >= amount:
            self.balance -= amount
            return True
        return False

    @classmethod
    def create(cls, username: str, password: str) -> 'User':
        with get_session() as session:
            new_user = User(username=username, password=password, balance=0)
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            return new_user

    @classmethod
    def get(cls, username: str, password: str) -> Optional['User']:
          with get_session() as session:
            user = session.query(User).filter_by(username=username, password=password).first()
            return user
