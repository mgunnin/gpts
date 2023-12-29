import unittest
from analysis import Analysis

class TestAnalysis(unittest.TestCase):
    def setUp(self):
        self.analysis = Analysis()
        self.player_stats = [
            {
                'participants': [
                    {
                        'stats': {
                            'kills': 10,
                            'deaths': 2,
                            'assists': 5,
                            'win': True,
                            'goldEarned': 15000,
                            'totalMinionsKilled': 200
                        }
                    }
                ]
            },
            {
                'participants': [
                    {
                        'stats': {
                            'kills': 5,
                            'deaths': 3,
                            'assists': 7,
                            'win': False,
                            'goldEarned': 12000,
                            'totalMinionsKilled': 180
                        }
                    }
                ]
            }
        ]

    def test_analyze(self):
        result = self.analysis.analyze(self.player_stats)
        self.assertEqual(result['Average Kills'], 7.5)
        self.assertEqual(result['Average Deaths'], 2.5)
        self.assertEqual(result['Average Assists'], 6)
        self.assertEqual(result['Win Rate'], 50)
        self.assertEqual(result['Average Gold Earned'], 13500)
        self.assertEqual(result['Average Minions Killed'], 190)


if __name__ == '__main__':
    unittest.main()
