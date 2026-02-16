"""
CalculatorTool — Migrate the Calculator to the Plugin Pattern
==============================================================
Convert the standalone calculator function from Lab 2 into a
BaseTool subclass. This makes it compatible with the ToolRegistry.

Steps:
  1. Implement all abstract properties (name, description, parameters)
  2. Implement the execute() method with the same logic as before
"""

from typing import Dict, Any
from base import BaseTool


class CalculatorTool(BaseTool):
    """A calculator tool that performs basic arithmetic operations."""

    @property
    def name(self) -> str:
        # TODO: Return the tool name "execute_calculation"
        return "execute_calculation"

    @property
    def description(self) -> str:
        # TODO: Return a clear description for the LLM
        # Hint: "Executes basic arithmetic operations (add, subtract, multiply, divide, pow)."
        return "Executes basic arithmetic operations (add, subtract, multiply, divide, pow)."


    @property
    def parameters(self) -> Dict[str, Any]:
        # TODO: Return the JSON Schema for the calculator
        # Hint: Copy the "parameters" section from CALCULATOR_SCHEMA in Lab 2
        # It should define: operation (enum), operand_a (number), operand_b (number)
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["add", "subtract", "multiply", "divide", "pow"],
                    "description": "The operation to perform."
                },
                "operand_a": {
                    "type": "number",
                    "description": "The first operand."
                },
                "operand_b": {
                    "type": "number",
                    "description": "The second operand."
                }
            },
            "required": ["operation", "operand_a", "operand_b"]
        }

    def execute(self, operation: str, operand_a: float, operand_b: float, **kwargs) -> Dict[str, Any]:
        """
        Perform the calculation.

        Returns:
            {"success": True/False, "result": <number or None>, "error": <str or None>}
        """
        # TODO: Implement the operation logic
        # - "add": operand_a + operand_b
        # - "subtract": operand_a - operand_b
        # - "multiply": operand_a * operand_b
        # - "divide": check for zero, then operand_a / operand_b
        # - "pow": operand_a ** operand_b
        # - else: return error "Unsupported operation"
        #
        # Wrap everything in try/except and always return structured dict
        try:
            if operation == "add":
                result = operand_a + operand_b
            elif operation == "subtract":
                result = operand_a - operand_b
            elif operation == "multiply":
                result = operand_a * operand_b
            elif operation == "divide":
                if operand_b == 0:
                    return {"success": False, "result": None, "error": "Division by zero is not allowed."}
                result = operand_a / operand_b
            elif operation == "pow":
                result = operand_a ** operand_b
            else:
                return {"success": False, "result": None, "error": f"Unsupported operation: {operation}"}

            return {"success": True, "result": result, "error": None}
        except Exception as e:
            return {"success": False, "result": None, "error": str(e)}


# Quick test
if __name__ == "__main__":
    calc = CalculatorTool()
    print(f"Name: {calc.name}")
    print(f"Schema: {calc.get_schema()}")
    print(f"Add: {calc.execute(operation='add', operand_a=10, operand_b=5)}")
    print(f"Divide by zero: {calc.execute(operation='divide', operand_a=10, operand_b=0)}")
