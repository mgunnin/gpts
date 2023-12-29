import unittest
from unittest.mock import patch, MagicMock
from openai import OpenAI

class TestChatGPT(unittest.TestCase):
    def setUp(self):
        self.model_name = 'gpt-4'
        self.token = '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'
        self.chatgpt = OpenAI(self.model_name, self.token)

    @patch('chatgpt.GPT3Completion')
    def test_generate_advice(self, mock_gpt3):
        # Mock the GPT-3 completion
        mock_gpt3.return_value.generate.return_value = 'Test advice'

        # Prepare the analysis result
        analysis_result = {
            'Average Kills': 10,
            'Average Deaths': 5,
            'Average Assists': 15,
            'Win Rate': 50,
            'Average Gold Earned': 10000,
            'Average Minions Killed': 200
        }

        # Call the method
        advice = self.chatgpt.generate_advice(analysis_result)

        # Check the result
        self.assertEqual(advice, 'Test advice')

        # Check if the GPT-3 completion was called with the correct arguments
        mock_gpt3.return_value.generate.assert_called_once_with(
            "The player's match statistics are as follows:\n"
            "Average Kills: 10\n"
            "Average Deaths: 5\n"
            "Average Assists: 15\n"
            "Win Rate: 50\n"
            "Average Gold Earned: 10000\n"
            "Average Minions Killed: 200\n"
            "What advice would you give to the player to improve their performance?",
            model=self.model_name
        )

    def test_prepare_prompt(self):
        # Prepare the analysis result
        analysis_result = {
            'Average Kills': 10,
            'Average Deaths': 5,
            'Average Assists': 15,
            'Win Rate': 50,
            'Average Gold Earned': 10000,
            'Average Minions Killed': 200
        }

        # Call the method
        prompt = self.chatgpt._prepare_prompt(analysis_result)

        # Check the result
        self.assertEqual(
            prompt,
            "The player's match statistics are as follows:\n"
            "Average Kills: 10\n"
            "Average Deaths: 5\n"
            "Average Assists: 15\n"
            "Win Rate: 50\n"
            "Average Gold Earned: 10000\n"
            "Average Minions Killed: 200\n"
            "What advice would you give to the player to improve their performance?"
        )


if __name__ == "__main__":
    unittest.main()