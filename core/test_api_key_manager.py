import unittest
from core.api_key_manager import GlobalAPIKeyManager
from datetime import date, timedelta

class TestGlobalAPIKeyManager(unittest.TestCase):
    def setUp(self):
        self.keys = ["key1", "AIzaSyB4JxfUFbL12IY0ktJquL0M9qOosS8hLqU", "key3"]
        GlobalAPIKeyManager.initialize(self.keys)

    def test_singleton(self):
        a = GlobalAPIKeyManager()
        b = GlobalAPIKeyManager()
        self.assertIs(a, b)

    def test_initialize_and_get_current_key(self):
        key = GlobalAPIKeyManager.get_current_key()
        self.assertIn(key, self.keys)

    def test_rotation_and_failover(self):
        first = GlobalAPIKeyManager.get_current_key()
        GlobalAPIKeyManager.mark_key_failed(first)
        second = GlobalAPIKeyManager.get_current_key()
        self.assertNotEqual(first, second)
        self.assertIn(second, self.keys)

    def test_all_keys_failed(self):
        for k in self.keys:
            GlobalAPIKeyManager.mark_key_failed(k)
        with self.assertRaises(Exception):
            GlobalAPIKeyManager.get_current_key()
        GlobalAPIKeyManager.force_reset_failed_keys()  # Reset for other tests

    def test_force_reset_failed_keys(self):
        GlobalAPIKeyManager.mark_key_failed(self.keys[0])
        GlobalAPIKeyManager.force_reset_failed_keys()
        self.assertEqual(len(GlobalAPIKeyManager._failed_keys), 0)

    def test_daily_reset(self):
        GlobalAPIKeyManager.mark_key_failed(self.keys[0])
        # Simulate a new day
        GlobalAPIKeyManager._last_reset_date = date.today() - timedelta(days=1)
        GlobalAPIKeyManager.get_current_key()  # Should trigger reset
        self.assertEqual(len(GlobalAPIKeyManager._failed_keys), 0)

    def test_get_detailed_status(self):
        status = GlobalAPIKeyManager.get_detailed_status()
        self.assertEqual(status['total_keys'], 3)
        self.assertIn('usage_stats', status)
        self.assertIn('current_key_prefix', status)

if __name__ == "__main__":
    unittest.main()
