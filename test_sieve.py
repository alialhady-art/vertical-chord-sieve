import unittest
from chord_sieve import count_primes

class TestVerticalChordSieve(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Warmup JIT compilation before running unit tests."""
        count_primes(1_000)

    def test_edge_cases(self):
        """Test bounds and edge conditions."""
        self.assertEqual(count_primes(0)[0], 0)
        self.assertEqual(count_primes(1)[0], 0)
        self.assertEqual(count_primes(2)[0], 1)
        self.assertEqual(count_primes(3)[0], 2)

    def test_known_pi_values(self):
        """Verify pi(N) accuracy against exact ground-truth values."""
        known_values = {
            10: 4,
            100: 25,
            1_000: 168,
            10_000: 1_229,
            100_000: 9_592,
            1_000_000: 78_498,
            10_000_000: 664_579,
            100_000_000: 5_761_455,
            1_000_000_000: 50_847_534,
        }

        for n, expected_pi in known_values.items():
            result, _ = count_primes(n)
            with self.subTest(N=n):
                self.assertEqual(
                    result, 
                    expected_pi, 
                    f"Mismatch for N = {n}: expected {expected_pi}, got {result}"
                )

if __name__ == "__main__":
    unittest.main()