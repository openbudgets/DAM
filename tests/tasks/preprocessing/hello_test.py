import unittest
from tasks.preprocessing import hello

class HelloTest(unittest.TestCase):

	def setUp(self):
		self.hello = hello.Hello()

	def test_hello(self):
		self.assertEqual(13, self.hello.hello(13))