from src.flamemodel import FlameModel, fields, BitMap


class UserPermissions(BitMap):
    id: int = fields(primary_key=True)
    can_read: bool = fields(flag=0)
    can_write: bool = fields(flag=1)
    can_delete: bool = fields(flag=2)
    can_admin: bool = fields(flag=3)

    def __repr__(self):
        return f'<UserPermissions id={self.id} read={self.can_read} write={self.can_write} delete={self.can_delete} admin={self.can_admin}>'


def example_set_permissions():
    # 设置用户权限
    permissions = UserPermissions(
        id=1,
        can_read=True,
        can_write=True,
        can_delete=False,
        can_admin=False
    )
    permissions.save()
    print('User permissions set successfully')


def example_get_permissions():
    permissions = UserPermissions.get(1)
    print('User permissions ===>', permissions)
    
    # 获取位图的元组表示
    bitmap = permissions.bitmap()
    print('Bitmap representation ===>', bitmap)


def example_count_permissions():
    count = UserPermissions.count_by(1)
    print('Number of enabled permissions ===>', count)
    
    # 或者通过实例获取
    permissions = UserPermissions.get(1)
    count = permissions.count()
    print('Instance permission count ===>', count)


def example_update_permissions():
    # 更新用户权限
    permissions = UserPermissions(
        id=1,
        can_read=True,
        can_write=True,
        can_delete=True,
        can_admin=True
    )
    permissions.save()
    print('Updated user permissions')


def example_bitwise_operations():
    # 创建两个用户权限进行位运算
    user1_perms = UserPermissions(
        id=1,
        can_read=True,
        can_write=True,
        can_delete=False,
        can_admin=False
    )
    user1_perms.save()
    
    user2_perms = UserPermissions(
        id=2,
        can_read=True,
        can_write=False,
        can_delete=True,
        can_admin=False
    )
    user2_perms.save()
    
    # 执行AND操作
    result_and = user1_perms.and_(user2_perms, 3)
    print('AND operation result ===>', result_and)
    
    # 执行OR操作
    result_or = user1_perms.or_(user2_perms, 4)
    print('OR operation result ===>', result_or)
    
    # 执行XOR操作
    result_xor = user1_perms.xor(user2_perms, 5)
    print('XOR operation result ===>', result_xor)


if __name__ == '__main__':
    print('BitMap Model'.center(60, '='))
    fm = FlameModel(
        'sync',
        'redis://:@localhost:6379/1'
    )
    print('FlameModel init success'.center(60, '='))

    example_set_permissions()
    example_get_permissions()
    example_count_permissions()
    example_update_permissions()
    example_get_permissions()
    example_bitwise_operations()

    print('BitMap example completed'.center(60, '='))