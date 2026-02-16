"""
ToolRegistry — Centralized Capability Management
==================================================
The registry is the heart of the tool system. It:
  1. Registers tool instances by name
  2. Generates schemas for the LLM API
  3. Executes tools safely with error boundaries
  4. Enforces rate limits and permissions

Steps:
  1. Implement register() — store tools and create rate limiters
  2. Implement get_schemas() — return all tool schemas
  3. Implement execute() — look up and run a tool safely
  4. Implement execute_secure() — add permission checks
"""

import logging
from typing import Dict, List, Any, Optional
from base import BaseTool
from manager import ToolRateLimiter

logger = logging.getLogger(__name__)


class SecurityError(Exception):
    """Raised when a security check fails."""
    pass


class ToolRegistry:
    """Centralized registry for managing and executing tools."""

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._limiters: Dict[str, ToolRateLimiter] = {}

    def register(self, tool: BaseTool, calls_per_minute: int = 60):
        """
        Registers a tool instance.

        Args:
            tool: A BaseTool instance to register
            calls_per_minute: Rate limit for this tool
        """
        # TODO: Store the tool in self._tools using tool.name as key
        # TODO: Create a ToolRateLimiter for this tool in self._limiters
        # TODO: Log the registration
        self._tools[tool.name] = tool
        self._limiters[tool.name] = ToolRateLimiter(calls_per_minute)
        logger.info(f"Registered tool '{tool.name}' with rate limit {calls_per_minute} calls/minute")


    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Returns a tool by name, or None if not found."""
        return self._tools.get(name)

    def get_schemas(self) -> List[Dict[str, Any]]:
        """
        Generates the list of schemas for the LLM API call.

        Returns:
            List of OpenAI-compatible tool schemas
        """
        # TODO: Return a list of get_schema() for each registered tool
        # Hint: [tool.get_schema() for tool in self._tools.values()]
        return [tool.get_schema() for tool in self._tools.values()]
    

    def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a tool by name with the given arguments.

        Steps:
          1. Look up the tool
          2. Check rate limit
          3. Execute with error boundary

        Returns:
            Tool result dict with success/result/error keys
        """
        # TODO: Look up the tool (return error dict if not found)
        # TODO: Check rate limiter (return error dict if rate limited)
        # TODO: Try to execute the tool, catch exceptions
        tool = self.get_tool(tool_name)
        if not tool:
            return {"success": False, "result": None, "error": f"Tool '{tool_name}' not found."}

        limiter = self._limiters.get(tool_name)
        if limiter and not limiter.is_allowed():
            return {"success": False, "result": None, "error": f"Rate limit exceeded for tool '{tool_name}'."}

        try:
            result = tool.execute(arguments)
            return {"success": True, "result": result, "error": None}
        except Exception as e:
            logger.exception(f"Error executing tool '{tool_name}': {e}")
            return {"success": False, "result": None, "error": str(e)}

    def execute_secure(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        user_permissions: List[str]
    ) -> Dict[str, Any]:
        """
        Executes a tool ONLY if the user has all required permissions.

        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments
            user_permissions: List of permissions the user has

        Returns:
            Tool result or access denied error
        """
        # TODO: Look up the tool
        # TODO: Check if user has all required permissions
        #   missing = [p for p in tool.permissions if p not in user_permissions]
        #   If missing, return {"success": False, "error": "Access Denied. Missing: ..."}
        # TODO: If permissions OK, delegate to self.execute()
        tool = self.get_tool(tool_name)
        if not tool:
            return {"success": False, "result": None, "error": f"Tool '{tool_name}' not found."}

        missing = [p for p in tool.permissions if p not in user_permissions]
        if missing:
            return {"success": False, "result": None, "error": f"Access Denied. Missing permissions: {missing}"}

        return self.execute(tool_name, arguments)


# =============================================================================
# Test the registry
# =============================================================================
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    from calculator_tool import CalculatorTool
    from filesystem import ListFilesTool

    registry = ToolRegistry()
    registry.register(CalculatorTool())
    registry.register(ListFilesTool())

    # Test schema generation
    print("Registered tools:")
    for schema in registry.get_schemas():
        print(f"  - {schema['function']['name']}")

    # Test execution
    print("\nCalculation test:")
    print(registry.execute("execute_calculation", {
        "operation": "multiply", "operand_a": 500, "operand_b": 0.15
    }))

    # Test secure execution
    print("\nSecurity test (no permissions):")
    print(registry.execute_secure("list_files", {"path": "."}, []))

    print("\nSecurity test (with permissions):")
    print(registry.execute_secure("list_files", {"path": "."}, ["filesystem:read"]))
