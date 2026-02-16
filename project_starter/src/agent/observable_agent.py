import asyncio
import json
import os
import time

import structlog
from litellm import acompletion, completion_cost
from pydantic import ValidationError

from src.observability.cost_tracker import CostTracker
from src.observability.loop_detector import AdvancedLoopDetector
from src.observability.tracer import AgentStep, AgentTracer, ToolCallRecord
from src.tools.registry import registry

logger = structlog.get_logger()


class ObservableAgent:
    """
    Production-grade agent with full observability.
    
    This agent implements the ReAct pattern (Reasoning + Acting) but enhances it 
    with "Observability" - the ability to track, trace, and debug the agent's 
    internal state and actions.
    """

    def __init__(
        self,
        model: str = None,
        max_steps: int = 10,
        agent_name: str = "ObservableAgent",
        verbose: bool = True,
        system_prompt: str = None,
        tools: list = None,
    ):
        self.model = model or os.getenv("MODEL_NAME", "gpt-4o")
        self.max_steps = max_steps
        self.agent_name = agent_name
        self.system_prompt = system_prompt
        self.tools = tools if tools is not None else registry.get_all_tools()

        # TODO: Initialize observability components
        # Observability includes:
        # 1. Tracing: Recording every step (reasoning, tool calls, results).
        # 2. Loop Detection: Preventing the agent from repeating the same actions.
        # 3. Cost Tracking: Monitoring token usage and cost.
        # self.tracer = ...
        # self.loop_detector = ...
        # self.cost_tracker = ...

        self.tracer = AgentTracer(verbose=verbose)
        self.loop_detector = AdvancedLoopDetector()
        self.cost_tracker = CostTracker()

    async def run(self, user_query: str) -> dict:
        """Execute the agent loop with full observability."""
        # TODO: Implement the agent loop
        # 1. Start trace and cost tracking
        # 2. Loop until max_steps
        # 3. Call LLM (using acompletion)
        # 4. Log completion and cost
        # 5. Handle tool calls (execute in parallel?)
        # 6. Check for loops
        # 7. Return final answer
        # 8. Handle errors and end trace

        self._current_query = user_query
        self._current_trace_id = self.tracer.start_trace(
            agent_name=self.agent_name,
            query=user_query,
            model=self.model,
        )
        self.cost_tracker.start_query(user_query)

        self._step_number = 0
        self.loop_detector.reset()

        messages = []

        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})

        messages.append({"role": "user", "content": user_query})

        final_answer = None

        try:
            while self._step_number < self.max_steps:
                self._step_number += 1
                step_start = time.time()

                response = await acompletion(
                    model=self.model,
                    messages=messages,
                    tools=[tool.to_openai_schema() for tool in self.tools],
                    tool_choice="auto",
                    max_tokens=500,
                )

                self.cost_tracker.log_completion(
                    step_number=self._step_number,
                    response=response,
                )

                message = response.choices[0].message
                tool_calls = getattr(message, "tool_calls", None)

                step = AgentStep(
                    step_number=self._step_number,
                    reasoning=message.content,
                )

                if not tool_calls:
                    final_answer = message.content

                    loop_check = self.loop_detector.check_output_stagnation(
                        final_answer
                    )
                    if loop_check.is_looping:
                        final_answer = loop_check.message

                    step.duration_ms = (time.time() - step_start) * 1000
                    self.tracer.log_step(self._current_trace_id, step)
                    break

                messages.append(
                    {
                        "role": "assistant",
                        "content": message.content,
                        "tool_calls": message.tool_calls,
                    }
                )

                for call in tool_calls:
                    tool_name = call.function.name
                    tool_args = call.function.arguments

                    loop_result = self.loop_detector.check_tool_call(
                        tool_name, tool_args
                    )

                    if loop_result.is_looping:
                        final_answer = loop_result.message
                        break

                    try:
                        args_dict = json.loads(tool_args)
                        tool = registry.get_tool(tool_name)
                        result = tool.execute(**args_dict)

                        tool_record = ToolCallRecord(
                            tool_name=tool_name,
                            tool_input=args_dict,
                            tool_output=str(result),
                            duration_ms=0,
                        )
                        step.tool_calls.append(tool_record)

                        messages.append(
                            {
                                "role": "tool",
                                "name": tool_name,
                                "content": str(result),
                            }
                        )

                    except ValidationError as ve:
                        final_answer = f"Tool validation error: {str(ve)}"
                        break
                    except Exception as e:
                        final_answer = f"Tool execution error: {str(e)}"
                        break

                step.duration_ms = (time.time() - step_start) * 1000
                self.tracer.log_step(self._current_trace_id, step)

                if final_answer:
                    break

            if not final_answer:
                final_answer = "Max steps reached without final answer."

            self.tracer.end_trace(
                self._current_trace_id,
                output=final_answer,
                status="completed",
            )

            self.cost_tracker.end_query()

            return {"answer": final_answer}

        except Exception as e:
            logger.error("agent_error", error=str(e))

            self.tracer.end_trace(
                self._current_trace_id,
                output="",
                status="error",
                error=str(e),
            )
            self.cost_tracker.end_query()

            return {"answer": f"Agent failed: {str(e)}"}
