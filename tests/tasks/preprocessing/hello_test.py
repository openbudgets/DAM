import unittest
import logging
from tasks.preprocessing import hello
from mock import Mock, patch

log = logging.getLogger(__name__)
log.level = logging.DEBUG


class HelloTest(unittest.TestCase):
    def setUp(self):
        self.hello = hello.Hello()
        log.info("huhu")

    def test_hello(self):
        my_mock = Mock()
        my_mock.testen.return_value = 3

        self.assertEqual(13, self.hello.hello(13))
        self.assertEqual(3, my_mock.testen())

    """
        @patch: package.module.class
    """

    @patch("hello_test.hello.requests")
    def test_huhu(self, mock_requests):
        mock_requests.get.return_value.content = "abcdefgh"
        print(self.hello.send_hello())
