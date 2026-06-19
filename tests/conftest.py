import os

# Health tests run without a RabbitMQ broker.
os.environ.setdefault("RABBITMQ_ENABLED", "false")
