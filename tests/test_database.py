import unittest
import json
from unittest.mock import patch, MagicMock
from database import Database

class TestDatabase(unittest.TestCase):
    @patch('psycopg2.connect')
    def setUp(self, mock_connect):
        self.mock_conn = MagicMock()
        self.mock_cur = MagicMock()

        mock_connect.return_value = self.mock_conn
        self.mock_conn.cursor.return_value = self.mock_cur

        self.db = Database('localhost', '5432', 'user', 'password', 'test_db')

    def test_save_player_stats(self):
        player_name = 'test_player'
        player_stats = {'wins': 10, 'losses': 5, 'kills': 100, 'deaths': 50}

        self.db.save_player_stats(player_name, player_stats)

        # Check if table creation query was executed
        self.mock_cur.execute.assert_any_call(
            "CREATE TABLE IF NOT EXISTS test_player ("
            "id SERIAL PRIMARY KEY,"
            "player_name VARCHAR(255),"
            "player_stats JSONB"
            ")"
        )

        # Check if insert query was executed
        self.mock_cur.execute.assert_any_call(
            "INSERT INTO test_player (player_name, player_stats) "
            "VALUES (%s, %s)",
            (player_name, json.dumps(player_stats))
        )

        # Check if commit was called
        self.mock_conn.commit.assert_called_once()

    def test_close(self):
        self.db.close()

        # Check if cursor close was called
        self.mock_cur.close.assert_called_once()

        # Check if connection close was called
        self.mock_conn.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
