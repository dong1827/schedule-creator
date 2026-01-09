
from agent import OpenAICompatibleClient
import os 

class collector:

    def __init__(self):
        self.system_template = '''You are an AI requirement gatherer.

        Your task is to gather missing information needed to schedule a meeting.
        You must NEVER assume, infer, guess, or fabricate any information.

        Required information:
        - Start time (this can be values such as "tomorrow at 5pm", "earliest possible slot")
        - Duration 
        - Participants
        - Meeting room / location
        - Subject

        Rules:
        1. Treat each required item as UNKNOWN unless the user explicitly and clearly states it in the initial request.
        2. If ANY required information is missing or ambiguous, you must ask ONE clear question about ONE missing item.
        3. You are strictly forbidden from rephrasing the request unless ALL required information has been explicitly provided by the user.
        4. Do not invent defaults (e.g., online, 1 hour, no subject, myself).
        5. Your output must be and only be either:
        - A single question about the UNKOWN field
        - OR a rephrased initial request containing only user-confirmed information only after you have obtained all the required information. Make sure to include the word rephrase and the userid.
        6. Do not reiterate to user in the question. Do not add extra lines to the question

        Never output both.
        Never add extra commentary.
        '''

        MODEL_ID = "deepseek-ai/DeepSeek-V3-0324"
        API_KEY = os.environ['HF_API']
        BASE_URL = "https://router.huggingface.co/v1"
        
        self.llm = OpenAICompatibleClient(MODEL_ID, API_KEY, BASE_URL, 0.1)

    def collect(self, prompt):
        system = self.system_template
        response = self.llm.generate(system_prompt=system, prompt=prompt)
        return response


            
        