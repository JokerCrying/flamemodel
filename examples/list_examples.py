from decimal import Decimal
from src.flamemodel import FlameModel, fields, List


class UserOrders(List):
    user_id: int = fields(primary_key=True)
    amount: Decimal = fields()
    should_pay: Decimal = fields()
    act_pay: Decimal = fields()
    buy_count: int = fields()

    def __repr__(self):
        items = [
            '<UserOrderItem'
        ]
        for k in self.model_fields_set:
            items.append(f'{k}={getattr(self, k)}')
        items.append('>')
        return ' '.join(items)


def example_append():
    orders = [
        UserOrders(user_id=1, amount=Decimal('10.00'), should_pay=Decimal('10.00'), act_pay=Decimal('9.99'),
                   buy_count=i)
        for i in range(10)
    ]
    for order in orders:
        order.append()


def example_get_all():
    orders = UserOrders.all(1)
    for order in orders:
        print('User Order pk=1 ===>', order)


def example_left_pop():
    order = UserOrders.left_pop(1)
    print('User Left Pop ===>', order)


def example_right_pop():
    order = UserOrders.right_pop(1)
    print('User Right Pop ===>', order)


def example_get():
    index = 0
    order = UserOrders.get(1, index)
    print('User Order index=0 ===>', order)


def example_length():
    print('Order length ===>', UserOrders.len(1))


if __name__ == '__main__':
    print('List Model'.center(60, '='))
    fm = FlameModel(
        'sync',
        'redis://:@localhost:6379/1'
    )
    print('FlameModel init success'.center(60, '='))

    example_append()
    example_length()
    example_get_all()
    example_left_pop()
    example_right_pop()
    example_length()

    print('Test Success'.center(60, '='))
