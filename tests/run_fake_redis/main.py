import fakeredis as fr

server = fr.TcpFakeServer(
    ('127.0.0.1', 6379),
    server_type='redis'
)

print('[*] Fake Redis Interface Adaptor Is Running In 127.0.0.1:6379')
server.serve_forever()
