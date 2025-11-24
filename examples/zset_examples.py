from src.flamemodel import FlameModel, fields, ZSet


class Player(ZSet):
    id: int = fields(primary_key=True)
    name: str = fields()
    player_score: float = fields(score_field=True)  # ZSet需要指定score字段

    def __repr__(self):
        return f'<Player id={self.id} name={self.name} score={self.player_score}>'


def example_add_players():
    players = [
        Player(id=1, name='Alice', player_score=100.0),
        Player(id=1, name='Bob', player_score=85.5),
        Player(id=1, name='Charlie', player_score=92.3),
        Player(id=1, name='David', player_score=78.9)
    ]
    Player.add(1, *players)
    print('Players added successfully')


def example_get_players_range():
    players = Player.range(1, 0, -1, withscores=True, reverse=True)
    print('Players sorted by score ===>', players)


def example_get_top_players():
    top_players = Player.top(1, 2, withscores=True)
    print('Top 2 players ===>', top_players)


def example_get_player_score():
    player = Player(id=1, name='Alice', player_score=100.0)
    score = Player.get_score(1, player)
    print('Alice\'s score ===>', score)


def example_increase_score():
    player = Player(id=1, name='Bob', player_score=85.5)
    new_score = player.incr_score(10.0)
    print('Bob\'s new score ===>', new_score)


def example_get_player_rank():
    player = Player(id=1, name='Charlie', player_score=92.3)
    rank = Player.get_rank(1, player, reverse=True)
    print('Charlie\'s rank ===>', rank)


def example_remove_player():
    player = Player(id=1, name='David', player_score=78.9)
    Player.remove(1, player)
    print('Removed David')


def example_get_size():
    size = Player.size(1)
    print('Players count ===>', size)


if __name__ == '__main__':
    print('ZSet Model'.center(60, '='))
    fm = FlameModel(
        'sync',
        'redis://:@localhost:6379/1'
    )
    print('FlameModel init success'.center(60, '='))

    example_add_players()
    example_get_players_range()
    example_get_top_players()
    example_get_player_score()
    example_increase_score()
    example_get_players_range()
    example_get_player_rank()
    example_remove_player()
    example_get_players_range()
    example_get_size()

    print('ZSet example completed'.center(60, '='))
