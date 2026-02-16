import logging
from dataclasses import dataclass, field
from urllib import response
# from litellm import completion_cost

logger = logging.getLogger(__name__)

@dataclass
class StepCost:
    step_number: int
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    is_tool_call: bool = False

@dataclass
class QueryCost:
    query: str
    steps: list[StepCost] = field(default_factory=list)
    total_cost_usd: float = 0.0
    total_input_tokens: int = 0
    total_output_tokens: int = 0

    def add_step(self, step: StepCost):
        self.steps.append(step)
        self.total_cost_usd += step.cost_usd
        self.total_input_tokens += step.input_tokens
        self.total_output_tokens += step.output_tokens

class CostTracker:
    """
    Tracks costs across agent executions.
    """
    def __init__(self):
        self.queries: list[QueryCost] = []
        self._current_query: QueryCost | None = None

    def start_query(self, query: str):
        self._current_query = QueryCost(query=query)

    def log_completion(self, step_number: int, response, is_tool_call: bool = False):
        """
        Log a completion response's cost.
        """
        # TODO: Implement this method
        # 1. Check if _current_query exists
        # 2. Extract usage stats from response
        # 3. Calculate cost (use litellm.completion_cost or fallback)
        # 4. create StepCost and add to query

        if not self._current_query:
            logger.warning("No active query to log completion for.")
            return

        usage = getattr(response, "usage", None)

        if usage:
            input_tokens = getattr(usage, "prompt_tokens", 0)
            output_tokens = getattr(usage, "completion_tokens", 0)
        else:
            input_tokens = 0
            output_tokens = 0

        model = getattr(response, "model", "unknown")

        cost_usd = (input_tokens + output_tokens) * 0.00001

        step_cost = StepCost(
            step_number=step_number,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd,
            is_tool_call=is_tool_call
        )

        self._current_query.add_step(step_cost)

    def end_query(self):
        if self._current_query:
            self.queries.append(self._current_query)
            self._current_query = None

    def print_cost_breakdown(self):
        # TODO: Print detailed cost breakdown
        for query_cost in self.queries:
            print(f"Query: {query_cost.query}")
            for step in query_cost.steps:
                tool_call_str = " (Tool Call)" if step.is_tool_call else ""
                print(f"  Step {step.step_number}: Model={step.model}, "
                      f"Input Tokens={step.input_tokens}, Output Tokens={step.output_tokens}, "
                      f"Cost=${step.cost_usd:.4f}{tool_call_str}")
            print(f"Total Cost for Query: ${query_cost.total_cost_usd:.4f}\n")
