from src.agent.observable_agent import ObservableAgent
from src.tools.registry import registry

#from project_starter.src.agent.observable_agent import ObservableAgent
#from project_starter.src.tools import registry


def create_researcher(model: str = "gpt-4o", max_steps: int = 15):
    """
    The Researcher: finds, retrieves, and extracts information.
    
    This function implements the Factory Pattern, returning a configured ObservableAgent
    specialized for research tasks.
    """
    # TODO: Implement this factory
    # 1. Define system prompt (e.g. "You are a world-class researcher...")
    # 2. Get research tools from registry (e.g. registry.get_tools_by_category("research"))
    # 3. Create and return ObservableAgent with these tools and prompt
    system_prompt = "You are a world-class researcher. Your task is to find and extract relevant information to answer the user's query. Use the available tools to search, retrieve, and analyze data. Always provide clear reasoning for your actions."
    tools = registry.get_tools_by_category("research")
    return ObservableAgent(model=model, max_steps=max_steps, agent_name="Researcher", system_prompt=system_prompt, tools=tools)


def create_analyst(model: str = "gpt-4o", max_steps: int = 20):
    """
    The Analyst: evaluates, cross-references, and identifies patterns.
    """
    # TODO: Implement this factory
    system_prompt = "You are a skilled analyst. Your task is to evaluate information, cross-reference sources, and identify patterns to provide insights. Use the available tools to analyze data and support your conclusions with clear reasoning."
    tools = registry.get_tools_by_category("analysis")
    return ObservableAgent(model=model, max_steps=max_steps, agent_name="Analyst", system_prompt=system_prompt, tools=tools)

def create_writer(model: str = "gpt-4o", max_steps: int = 4):
    """
    The Writer: synthesizes analysis into polished, readable output.
    """
    # TODO: Implement this factory
    system_prompt = "You are a talented writer. Your task is to synthesize information and analysis into polished, readable output. Use the available tools to enhance your writing and ensure clarity and coherence in your final response."
    tools = registry.get_tools_by_category("writing")
    return ObservableAgent(model=model, max_steps=max_steps, agent_name="Writer", system_prompt=system_prompt, tools=tools)