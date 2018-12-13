from django.test import TestCase
from selenium import webdriver
from unittest.mock import MagicMock, Mock, patch
import unittest
from myproject import client


def mply(x, y):
    return x * y

class TestProducer(TestCase):
    def setUp(self):
        print("setUp")

    @patch('mply')
    def test_multiply(self, mock_multiply):
        mock_multiply.return_value = 34
        self.assertEqual(client.mply(4, 5), 20)


if __name__ == '__main__':

    suite = unittest.TestLoader().loadTestsFromTestCase(TestProducer)

    unittest.TextTestRunner(verbosity=2).run(suite)

