from src.flamemodel import FlameModel, fields, String
from typing import Optional


class User(String):
    id: int = fields(primary_key=True)
    username: str = fields(unique=True)
    age: int = fields()
    address: Optional[str] = fields()

    def __repr__(self):
        return f'<User id={self.id} username={self.username} age={self.age} address={self.address}>'


def example_user_save():
    user = User(id=1, username='Jack', age=18, address=None)
    user.save()


def example_user_update():
    user = User.get(1)
    user.age = 19
    user.address = 'USA'
    user.save()


def example_user_delete():
    user = User.get(1)
    user.delete()


def example_user_get():
    user = User.get(1)
    print('user ===>', user)


if __name__ == '__main__':
    print('String Model'.center(60, '='))
    fm = FlameModel(
        'sync',
        'redis://:@localhost:6379/1'
    )
    print('FlameModel init success'.center(60, '='))

    example_user_save()
    print('User Save Success'.center(60, '='))
    example_user_get()  # id=1 name=Jack age=18 address=None

    example_user_update()
    print('User update success'.center(60, '='))
    example_user_get()  # id=1 name=Jack age=19 address=USA

    example_user_delete()
    print('User delete success'.center(60, '='))
    example_user_get()  # None
