from src.flamemodel import FlameModel, fields, Stream
from typing import Optional
from datetime import datetime


class Message(Stream):
    stream_id: str = fields(primary_key=True, entry=True)  # Stream需要指定entry字段作为消息ID
    sender: str = fields()
    content: str = fields()
    timestamp: str = fields()

    def __repr__(self):
        return f'<Message id={self.stream_id} sender={self.sender} content={self.content} timestamp={self.timestamp}>'


def example_add_messages():
    # 添加消息到流
    messages = [
        Message(
            stream_id="*",  # 使用"*"让Redis自动生成ID
            sender="Alice",
            content="Hello everyone!",
            timestamp=str(datetime.now().timestamp())
        ),
        Message(
            stream_id="*",
            sender="Bob",
            content="Hi Alice!",
            timestamp=str(datetime.now().timestamp())
        )
    ]
    
    for msg in messages:
        msg_id = msg.save()
        print(f'Message added with ID: {msg_id}')
    
    return messages[0].stream_id.split("-")[0]  # 返回第一个消息的前缀ID用于后续查询


def example_read_stream(prefix_id):
    # 读取流中的消息
    streams = {1: f"{prefix_id}-0"}  # 从指定ID开始读取
    results = Message.read(streams, count=10)
    print('Stream messages ===>')
    for stream_key, messages in results.items():
        print(f'Stream {stream_key}:')
        for msg_id, msg in messages:
            print(f'  {msg_id}: {msg}')


def example_range_stream():
    # 获取流中的消息范围
    messages = Message.range(1, count=10)
    print('Messages in range ===>')
    for msg_id, msg in messages:
        print(f'  {msg_id}: {msg}')


def example_reverse_range_stream():
    # 反向获取流中的消息范围
    messages = Message.reverse_range(1, count=10)
    print('Messages in reverse range ===>')
    for msg_id, msg in messages:
        print(f'  {msg_id}: {msg}')


def example_get_length():
    length = Message.length(1)
    print('Stream length ===>', length)


def example_trim_stream():
    # 修剪流，只保留最新的2条消息
    trimmed_count = Message.trim(1, max_length=2, approximate=True)
    print('Trimmed messages count ===>', trimmed_count)


def example_delete_message():
    # 获取现有消息并删除第一条
    messages = Message.range(1, count=1)
    if messages:
        msg_id, _ = messages[0]
        deleted_count = Message.delete_entries(1, msg_id)
        print(f'Deleted {deleted_count} message(s)')


if __name__ == '__main__':
    print('Stream Model'.center(60, '='))
    fm = FlameModel(
        'sync',
        'redis://:@localhost:6379/1',
        connect_options={
            'decode_responses': True
        }
    )
    print('FlameModel init success'.center(60, '='))

    prefix_id = example_add_messages()
    example_read_stream(prefix_id)
    example_range_stream()
    example_reverse_range_stream()
    example_get_length()
    example_delete_message()
    example_get_length()
    example_trim_stream()
    example_get_length()

    print('Stream example completed'.center(60, '='))