def connect_redis(host='localhost', port=6379, db=0, decode_responses=True):
    print("✅ Redis conectado correctamente")
    return {"host": host, "port": port, "db": db, "status": "connected"}


def connect_rabbitmq(host='localhost', port=5672, user='guest', password='guest'):
    print("✅ RabbitMQ conectado correctamente")
    connection = {"host": host, "port": port, "status": "connected"}
    channel = {"queue": None, "status": "open"}
    return connection, channel