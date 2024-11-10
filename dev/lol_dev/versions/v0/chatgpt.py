import openai

class ChatGPT:
    def __init__(self, model_name, token):
        self.model_name = model_name
        openai.api_key = token

    def generate_advice(self, analysis_result):
        # Prepare the prompt for GPT
        prompt = self._prepare_prompt(analysis_result)

        # Generate the advice using GPT
        advice = openai.Completion.create(engine=self.model_name, prompt=prompt)

        return advice.choices[0].text.strip()

    def _prepare_prompt(self, analysis_result):
        # Convert the analysis result into a string
        analysis_str = "\n".join(f"{k}: {v}" for k, v in analysis_result.items())

        # Prepare the prompt
        prompt = f"The player's match statistics are as follows:\n{analysis_str}\nWhat advice would you give to the player to improve their performance?"

        return prompt
