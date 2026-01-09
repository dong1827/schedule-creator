from agent import OpenAICompatibleClient
import os
import ast

class planner:

    def __init__(self):
        self.prompt_template = '''You are an intelligent AI planner. Your job is to break down user's request into a feasible plan that is consists of 
        smaller and simplier subtasks. Every subtask must be independent, executable, and can be done through a single use of one of the tools.
        The subtasks must also be in logical order.
        You must not assume anything. 

        request:{request}

        # available tools: 
        - get_date(): Get the current date. 
        - get_contact(name:string): get the email of a person
        - create_event(userid:string, start:string, end:string, participants:list, subject:str, location:str, description:str = ""): creates an event at specific time with the participant list. start and end time are in ISO format
          
        your output is a python list, in which every element is the tool name with a description of the arguments. your output/plan must be in the following format: 
        ```python 
        ["tool1(description for args): explaination", "tool2(description for args): explaination"...]   
        ``` 
        note the ```python``` affix is required. 

        
        '''

        MODEL_ID = "deepseek-ai/DeepSeek-V3-0324"
        API_KEY = os.environ['HF_API']
        BASE_URL = "https://router.huggingface.co/v1"
        
        self.llm = OpenAICompatibleClient(MODEL_ID, API_KEY, BASE_URL)

    def plan(self, request):
        prompt = self.prompt_template.format(request=request)

        print("Generating a plan...")
        print("--------------------")

        response = self.llm.generate(prompt=prompt)
        print(response)
        
        try:
            # find the text inbetween ```python```
            plan_str = response.split("```python")[1].split("```")[0].strip()
            # convert to list
            plan = ast.literal_eval(plan_str)
            return plan if isinstance(plan, list) else []
        except (ValueError, SyntaxError, IndexError) as e:
            print(f"error in parsing: {e}")
            print(f"original text: {response}")
            return []
        except Exception as e:
            print(f"unknown error: {e}")
            return []
        
        