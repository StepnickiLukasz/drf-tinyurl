from unittest.mock import patch

from django.test import SimpleTestCase, override_settings

from tiny_api.managers import TinyUrlManager


@override_settings(
    REDIS_CONNECTIONS={
        "default": {
            "REDIS_HOST": "localhost",
            "REDIS_PORT": 6379,
            "REDIS_DB": 0,
            "KEY_EXPIRATION_TIME": 3600,
        }
    },
    SHORT_URL_LINK_GENERATOR_SETTINGS={
        "ALLOWED_CHARS": "abc123",
        "URL_LENGTH": 6,
    },
)
class TinyUrlManagerTests(SimpleTestCase):

    def setUp(self):
        super().setUp()
        self.manager = TinyUrlManager("default")

    def test_init_fails_when_required_redis_key_missing(self):
        with self.assertRaises(AssertionError):
            with override_settings(
                REDIS_CONNECTIONS={
                    "default": {
                        "REDIS_HOST": "localhost",
                        "REDIS_PORT": 6379,
                        "REDIS_DB": 0,
                    }
                }
            ):
                TinyUrlManager("default")

    @patch("tiny_api.managers.redis.StrictRedis")
    def test_get_redis_connection_creates_connection(self, redis_mock):
        connection = self.manager.get_redis_connection()
        redis_mock.assert_called_once_with(host="localhost", port=6379, db=0, decode_responses=True)
        self.assertEqual(connection, redis_mock.return_value)

    @patch("tiny_api.managers.random.choice")
    def test_generate_short_url(self, choice_mock):
        choice_mock.return_value = "a"
        result = self.manager.generate_short_url()
        self.assertEqual(result, "aaaaaa")
        self.assertEqual(choice_mock.call_count, 6)

    @patch("tiny_api.managers.redis.StrictRedis")
    def test_set_short_url_creates_new_entry(self, redis_mock):
        redis_conn = redis_mock.return_value
        redis_conn.set.return_value = True
        with patch.object(self.manager, "generate_short_url", return_value="abc123"):
            result = self.manager.set_short_url("https://example.com")
        self.assertEqual(result, "abc123")
        redis_conn.set.assert_called_once_with("abc123", "https://example.com", nx=True, ex=3600)

    @patch("tiny_api.managers.redis.StrictRedis")
    def test_set_short_url_retries_when_key_exists(self, redis_mock):
        redis_conn = redis_mock.return_value
        redis_conn.set.side_effect = [None, True]
        with patch.object(self.manager, "generate_short_url", side_effect=["taken1", "free1"]):
            result = self.manager.set_short_url("https://example.com")

        self.assertEqual(result, "free1")
        self.assertEqual(redis_conn.set.call_count, 2)
        redis_conn.set.assert_any_call("taken1", "https://example.com", nx=True, ex=3600)
        redis_conn.set.assert_any_call("free1", "https://example.com", nx=True, ex=3600)

    @patch("tiny_api.managers.redis.StrictRedis")
    def test_get_full_url_returns_url(self, redis_mock):
        redis_conn = redis_mock.return_value
        redis_conn.get.return_value = ("https://example.com")
        result = self.manager.get_full_url("abc123")
        self.assertEqual(result, "https://example.com")
        redis_conn.get.assert_called_once_with("abc123")

    @patch("tiny_api.managers.redis.StrictRedis")
    def test_get_full_url_returns_none_when_missing(self, redis_mock):
        redis_conn = redis_mock.return_value
        redis_conn.get.return_value = None
        result = self.manager.get_full_url("unknown")
        redis_conn.get.assert_called_once_with("unknown")
        self.assertIsNone(result)
