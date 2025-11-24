from src.flamemodel import FlameModel, fields, Set


class Tag(Set):
    id: int = fields(primary_key=True)
    name: str = fields()

    def __repr__(self):
        return f'<Tag id={self.id} name={self.name}>'


def example_add_tags():
    tags = [
        Tag(id=1, name='Python'),
        Tag(id=1, name='Redis'),
        Tag(id=1, name='FlameModel'),
        Tag(id=1, name='Database')
    ]
    for tag in tags:
        tag.save()
    print('Tags added successfully')


def example_get_members():
    members = Tag.members(1)
    print('Set members ===>', members)


def example_check_membership():
    tag = Tag(id=1, name='Python')
    is_member = Tag.contains(1, tag)
    print('Is "Python" a member ===>', is_member)


def example_get_size():
    size = Tag.size(1)
    print('Set size ===>', size)


def example_remove_tag():
    tag = Tag(id=1, name='Database')
    tag.remove()
    print('Removed "Database" tag')


def example_pop_random():
    random_tag = Tag.pop_random(1)
    print('Randomly popped tag ===>', random_tag)


def example_get_random():
    random_tags = Tag.random(1, 2)
    print('Random tags ===>', random_tags)


if __name__ == '__main__':
    print('Set Model'.center(60, '='))
    fm = FlameModel(
        'sync',
        'redis://:@localhost:6379/1'
    )
    print('FlameModel init success'.center(60, '='))

    example_add_tags()
    example_get_members()
    example_check_membership()
    example_get_size()
    example_pop_random()
    example_get_members()
    example_remove_tag()
    example_get_members()
    example_get_random()

    print('Set example completed'.center(60, '='))