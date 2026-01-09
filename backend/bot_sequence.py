from collector import collector
from planner import planner
from executor import executor
from collector import collector
import tools
import json

available_tools = { 
    "get_contact": tools.get_contact,
    "get_date": tools.get_date,
    "create_event": tools.create_event,
}

def use_tool(action_str:str):
    action_str = action_str.strip()
    if action_str.startswith("```json"):
        action_str = action_str[len("```json"):].strip()
    if action_str.endswith("```"):
        action_str = action_str[:-3].strip()
        
    payload = json.loads(action_str)
    tool_name = payload["tool"]
    kwargs = payload["args"]
        
    if tool_name in available_tools:      
        obs = available_tools[tool_name](**kwargs)
    else: 
        obs = f"error: undefined tool '{tool_name}"

    return obs

def execute_sequence(message):
    llm_collector = collector()
    result = llm_collector.collect(message)
    if "rephrase" not in result.lower(): 
        return result

    llm_planner = planner()
    plan = llm_planner.plan(result)
    llm_executor = executor()
    history = ""
    for i, step in enumerate(plan): 
        action_str = llm_executor.execute(request=result, plan=plan, history=history, step=step)
        obs = use_tool(action_str)
        history+= f"{action_str}\nobservation: {obs}\n\n"

    return "finished"