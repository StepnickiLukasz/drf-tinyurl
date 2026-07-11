import random

import redis
from django.conf import settings


class TinyUrlManager:
    # Manager created to handle retrieving and creating short_url:full_url data from Redis database

    def __init__(self, redis_conn_profile):
        self.connection = None
        self.redis_connection = settings.REDIS_CONNECTIONS.get(redis_conn_profile)
        for required_key in ("REDIS_HOST", "REDIS_PORT", "REDIS_DB", "KEY_EXPIRATION_TIME"):
            assert required_key in self.redis_connection.keys()
        self.allowed_chars = settings.SHORT_URL_LINK_GENERATOR_SETTINGS.get("ALLOWED_CHARS")
        self.url_length = settings.SHORT_URL_LINK_GENERATOR_SETTINGS.get("URL_LENGTH")

    def get_redis_connection(self):
        if not self.connection:
            self.connection = redis.StrictRedis(
                host=self.redis_connection.get("REDIS_HOST"),
                port=self.redis_connection.get("REDIS_PORT"),
                db=self.redis_connection.get("REDIS_DB"),
                decode_responses=True,
            )
        return self.connection

    def generate_short_url(self):
        return ''.join(random.choice(self.allowed_chars) for _ in range(self.url_length))

    def set_short_url(self, full_url):
        conn = self.get_redis_connection()
        short_url = None
        result = False
        while not result:  # retry if key already taken
            short_url = self.generate_short_url()
            result = conn.set(short_url, full_url, nx=True, ex=self.redis_connection.get("KEY_EXPIRATION_TIME"))
        return short_url

    def get_full_url(self, short_url):
        conn = self.get_redis_connection()
        return conn.get(short_url)
