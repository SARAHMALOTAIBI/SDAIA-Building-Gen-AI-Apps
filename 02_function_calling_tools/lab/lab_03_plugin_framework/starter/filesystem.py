"""
ListFilesTool — A Secure Filesystem Tool
==========================================
Lists files in a directory, but only if:
  1. The user has "filesystem:read" permission
  2. The path passes sanitization (no directory traversal)

Steps:
  1. Implement the execute() method
  2. Use PathSanitizer to validate the path
  3. List files and return structured result
"""

import os
from typing import Dict, Any
from base import BaseTool
from security import PathSanitizer, SecurityError


class ListFilesTool(BaseTool):
    """Lists files in a directory with security controls."""

    # The allowed root directory for file operations
    BASE_DIR = "."

    @property
    def name(self) -> str:
        return "list_files"

    @property
    def description(self) -> str:
        return "Lists files in a specific directory. Requires filesystem:read permission."

    @property
    def permissions(self) -> list[str]:
        return ["filesystem:read"]

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The directory path to list files from."
                }
            },
            "required": ["path"]
        }

    def execute(self, path: str = ".", **kwargs) -> Dict[str, Any]:
        """
        List files in the given directory.

        Steps:
          1. Validate the path using PathSanitizer
          2. List the directory contents with os.listdir()
          3. Return structured result

        Returns:
            {"success": True, "result": [list of filenames], "error": None}
            or on error: {"success": False, "result": None, "error": "..."}
        """
        # TODO: Validate path with PathSanitizer.validate_safe_path(self.BASE_DIR, path)
        # TODO: List files with os.listdir(safe_path)
        # TODO: Return structured result
        # TODO: Catch SecurityError and other exceptions
        try:
            # Validate the path
            safe_path = PathSanitizer.validate_safe_path(self.BASE_DIR, path)

            # List files in the directory
            files = os.listdir(safe_path)

            return {"success": True, "result": files, "error": None}
        except SecurityError as se:
            return {"success": False, "result": None, "error": f"Security error: {str(se)}"}
        except Exception as e:
            return {"success": False, "result": None, "error": f"Error: {str(e)}"}


# Quick test
if __name__ == "__main__":
    tool = ListFilesTool()
    print(f"Name: {tool.name}")
    print(f"Permissions: {tool.permissions}")
    print(f"Schema: {tool.get_schema()}")

    # Test listing current directory
    print(f"\nList '.': {tool.execute(path='.')}")

    # Test directory traversal attack
    print(f"\nAttack '../..': {tool.execute(path='../..')}")
