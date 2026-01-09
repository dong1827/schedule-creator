from agent import OpenAICompatibleClient
import os

class executor:

    def __init__(self):
        self.prompt_template = '''You are an intelligent AI executor. Your job is to execute the tasks within the plan step by step.
        you will receive the original request, the plan, and the historical steps and results. Please focus on executing the current step. 
        You must execute the current step by calling one of the tools and figure out the correct argument for the tool. Make sure each argument is surrounded by quotes.
        Your output should be a json data with the correct tool name and its correct arguments. So the json would contain two keys, tool and args.
        DO NOT OUTPUT ANYTHING OTHER THAN JSON DATA!

        # available tools: 
        - get_date(): Get the current date. 
        - get_contact(name:string): get the email of a person. If there's no other participants, skip this step by calling get_contact(myself)
        - create_event(user_id:string, start:string, end:string, participants:list, subject:str, location:str, description:str = ""): creates an event at specific time with the participant list. start and end time are in ISO format.
        
        # orignal request:
        {request}

        # full plan: 
        {plan}

        #historical steps and results: 
        {history}

        #current step: 
        {step}

        please output only what matters to current step
        '''

        MODEL_ID = "deepseek-ai/DeepSeek-V3-0324"
        API_KEY = os.environ['HF_API']
        BASE_URL = "https://router.huggingface.co/v1"
        
        self.llm = OpenAICompatibleClient(MODEL_ID, API_KEY, BASE_URL)

    def execute(self, request, plan, history, step):
        prompt = self.prompt_template.format(request=request, plan=plan, history=history, step=step)

        print("Generating...")

        response = self.llm.generate(prompt=prompt)
        print(response)
        return response