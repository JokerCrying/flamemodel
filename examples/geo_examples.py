from src.flamemodel import FlameModel, fields, Geo


class Location(Geo):
    id: int = fields(primary_key=True)
    name: str = fields(member_field=True)  # Geo需要指定member字段
    longitude: float = fields(lng_field=True)  # Geo需要指定经度字段
    latitude: float = fields(lat_field=True)   # Geo需要指定纬度字段

    def __repr__(self):
        return f'<Location id={self.id} name={self.name} longitude={self.longitude} latitude={self.latitude}>'


def example_add_locations():
    locations = [
        Location(id=1, name='Beijing', longitude=116.4074, latitude=39.9042),
        Location(id=1, name='Shanghai', longitude=121.4737, latitude=31.2304),
        Location(id=1, name='Guangzhou', longitude=113.2644, latitude=23.1291),
        Location(id=1, name='Shenzhen', longitude=113.9416, latitude=22.5444)
    ]
    
    Location.add(1, *locations)
    print('Locations added successfully')


def example_search_radius():
    # 搜索北京附近的地点（半径1000公里）
    nearby_locations = Location.search_radius(
        pk=1,
        longitude=116.4074,  # 北京经度
        latitude=39.9042,    # 北京纬度
        radius=1000,         # 1000公里半径
        unit='km',
        count=10
    )
    print('Nearby locations ===>')
    for loc in nearby_locations:
        print(f'  {loc}')


def example_get_location():
    # 根据成员名称获取位置信息
    location = Location.get_by_member(1, 'Shanghai')
    print('Shanghai location ===>', location)


def example_save_single_location():
    # 保存单个位置
    location = Location(id=1, name='Hangzhou', longitude=120.1551, latitude=30.2741)
    location.save()
    print('Hangzhou location saved')


def example_delete_location():
    # 删除位置（需要有完整的对象）
    location = Location(id=1, name='Guangzhou', longitude=113.2644, latitude=23.1291)
    result = location.delete_self()
    print('Deleted Guangzhou, result ===>', result)


if __name__ == '__main__':
    print('Geo Model'.center(60, '='))
    fm = FlameModel(
        'sync',
        'redis://:@localhost:6379/1'
    )
    print('FlameModel init success'.center(60, '='))

    example_add_locations()
    example_search_radius()
    example_get_location()
    example_save_single_location()
    example_search_radius()
    example_delete_location()
    example_search_radius()

    print('Geo example completed'.center(60, '='))
