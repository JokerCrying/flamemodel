import fakeredis as fr

server = fr.TcpFakeServer(
    ('127.0.0.1', 6379),
    server_type='redis'
)

server.serve_forever()
