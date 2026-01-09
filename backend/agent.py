from openai import OpenAI

class OpenAICompatibleClient: 
    """
    Client that is compatible to any LLM openAI socket
    """

    def __init__(self, model:str, api_key: str, base_url:str, temperature=0.1):
        self.model = model 
        self.temperature = temperature
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def generate(self, prompt: str, system_prompt: str ="") -> str: 
        """
        Use LLM API to generate response
        """

        try: 
            messages = [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': prompt}
            ]

            response = self.client.chat.completions.create(
                model = self.model,
                messages = messages,
                temperature=self.temperature,
                stream = False 
            )

            answer = response.choices[0].message.content
            return answer
        
        except Exception as e: 
            print(f"error when trying to connect to LLM API: {e}")
            return "error: error when trying to connect to LLM server"