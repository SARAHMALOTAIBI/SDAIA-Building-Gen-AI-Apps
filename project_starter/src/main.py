import asyncio
import os
import sys
import time

from dotenv import load_dotenv

from src.agent.specialists import create_researcher, create_analyst, create_writer
from src.observability.tracer import tracer # TODO: Unleash the tracer
#from src.observability.cost_tracker import CostTracker

# Load environment variables
load_dotenv(dotenv_path=".env")
print("LOADED KEY:", os.getenv("OPENAI_API_KEY"))

async def main():
    """
    Main entry point for the AI Agent system.
    """
    # 1. Get the query
    if len(sys.argv) < 2:
        print("Usage: python -m src.main \"Your research query\"")
        sys.exit(1)

    query = sys.argv[1]
    print(f"Starting research on: {query}")

    # TODO: Initialize your agents here
    # Use the Factory Pattern to create agents.
    # The 'create_researcher' function (and others) acts as a factory, encapsulating 
    # the creation logic (prompt selection, tool assignment) for each agent type.
    # researcher = create_researcher()
    # analyst = create_analyst()
    # writer = create_writer()
    researcher = create_researcher()
    analyst = create_analyst()
    writer = create_writer()
    agents = [researcher, analyst, writer]  
    agent_names = [agent.agent_name for agent in agents]
    print(f"Initialized agents: {', '.join(agent_names)}")

    
    # TODO: Create the orchestrator or main loop
    # In the final project, we might use an ArchitectureDecisionEngine here to decide
    # which agent architecture (Single vs Multi-Agent) to run. 
    # For this starter, you can implement a simple linear chain (Researcher -> Analyst -> Writer)
    # or a loop.
    # ...
    start_time = time.time()

    researcher_result = await researcher.run(query)
    analyst_result = await analyst.run(researcher_result.get("answer", ""))
    writer_result = await writer.run(analyst_result.get("answer", ""))

    end_time = time.time()

    print(f"Final Output:\n{writer_result.get('answer', '')}")
    print(f"Total Execution Time: {end_time - start_time:.2f} seconds")
    print("\nCost Breakdown:")
    researcher.cost_tracker.print_cost_breakdown()
    analyst.cost_tracker.print_cost_breakdown()
    writer.cost_tracker.print_cost_breakdown()
    print("Project Starter: Not implemented yet. Check the TODOs!")

if __name__ == "__main__":
    asyncio.run(main())


