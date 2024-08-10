import unittest
from benchmarks.linux import run_linux_checks

class TestLinuxChecks(unittest.TestCase):
    
    def test_run_linux_checks(self):
        results = run_linux_checks()
        self.assertIsInstance(results, dict)
        self.assertIn('SSH Root Login Disabled', results)
        self.assertIn('Firewall Active', results)
        # Add more tests for other checks
        
    # Add individual tests for each check if needed

if __name__ == '__main__':
    unittest.main()
