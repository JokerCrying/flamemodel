from decimal import Decimal

from src.flamemodel import FlameModel, fields, Hash


class UserMallCar(Hash):
    user_id: int = fields(primary_key=True)
    product_id: int = fields(hash_field=True)
    product_name: str = fields()
    buy_time_price: Decimal = fields()
    total_stock: int = fields()

    def __repr__(self):
        items = [
            '<UserMallCar'
        ]
        for key in self.model_fields_set:
            items.append(f'{key}={getattr(self, key)}')
        items.append('>')
        return ' '.join(items)


def example_save():
    mall_car1 = UserMallCar(user_id=1, product_id=1,
                            product_name='iPhone 17 Pro Max', buy_time_price=Decimal('7999.00'),
                            total_stock=1000)
    mall_car1.save()
    mall_car2 = UserMallCar(user_id=1, product_id=2,
                            product_name='iPhone 17 Air', buy_time_price=Decimal('6999.00'),
                            total_stock=10)
    mall_car2.save()


def example_update():
    mall_car1 = UserMallCar.get(1, 1)
    mall_car1.total_stock -= 1
    mall_car1.save()


def example_delete():
    mall_car1 = UserMallCar.get(1, 1)
    mall_car1.hash_delete()


def example_get_all():
    all_product = UserMallCar.get_all(1)
    print('All Product pk=1 ===>', all_product)


def example_keys():
    keys = UserMallCar.keys(1)
    print('Keys pk=1 ===>', keys)


def example_values():
    values = UserMallCar.values(1)
    print('Values pk=1 ===>', values)


def example_get():
    for pid in [1, 2]:
        item = UserMallCar.get(1, pid)
        print(f'User Mall Card pid={pid} ===>', item)


if __name__ == '__main__':
    print('Hash Model'.center(60, '='))
    fm = FlameModel(
        'sync',
        'redis://:@localhost:6379/1'
    )
    print('FlameModel init success'.center(60, '='))

    example_save()
    example_get()
    example_get_all()
    example_keys()
    example_values()
    example_update()
    example_get()
    example_delete()
    example_get()
    example_get_all()
    example_keys()
    example_values()

    print('Test success'.center(60, '='))
