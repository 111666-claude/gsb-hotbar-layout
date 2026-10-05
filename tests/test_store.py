import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hotbar.store import Layout  # noqa: E402


class LayoutTest(unittest.TestCase):
    def test_place_then_read(self):
        layout = Layout(4)
        self.assertTrue(layout.place("r1", 0, "slash"))
        self.assertEqual(layout.cells[0], "slash")

    def test_move_inside_bounds(self):
        layout = Layout(4)
        layout.place("r1", 0, "slash")
        layout.move("r2", 0, 1, 2)
        self.assertEqual(layout.cells[2], "slash")

    def test_stats_on_empty_layout(self):
        self.assertEqual(Layout(4).stats(), (0, 0))

    def test_work_starts_at_zero(self):
        self.assertEqual(Layout(4).work_count(), 0)


if __name__ == "__main__":
    unittest.main()
