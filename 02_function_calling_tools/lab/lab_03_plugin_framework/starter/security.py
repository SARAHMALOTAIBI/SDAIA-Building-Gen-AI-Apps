"""
PathSanitizer — Prevent Directory Traversal Attacks
=====================================================
When an LLM controls file paths, you MUST validate that the
path stays within the allowed directory. An LLM might be tricked
into requesting "../../etc/passwd".

Steps:
  1. Implement validate_safe_path() — resolve and check paths
"""

import os


class SecurityError(Exception):
    """Raised when a security check fails (e.g., path traversal)."""
    pass


class PathSanitizer:
    """Validates file paths to prevent directory traversal attacks."""

    @staticmethod
    def validate_safe_path(base_dir: str, target_path: str) -> str:
        """
        Ensures target_path resolves to a location within base_dir.

        Args:
            base_dir: The allowed root directory (e.g., "./workspace")
            target_path: The path requested (e.g., "reports/q1.txt" or "../../etc/passwd")

        Returns:
            The resolved absolute path if safe

        Raises:
            SecurityError: If the path escapes base_dir

        Algorithm:
          1. Get absolute path of base_dir
          2. Join base_dir + target_path, then get absolute path
          3. Check if the resolved path starts with base_dir
          4. If not, raise SecurityError
        """
        # TODO: Implement path validation
        # abs_base = os.path.abspath(base_dir)
        # abs_target = os.path.abspath(os.path.join(base_dir, target_path))
        # if not abs_target.startswith(abs_base):
        #     raise SecurityError(f"Path traversal blocked: {target_path}")
        # return abs_target
        abs_base = os.path.abspath(base_dir)
        abs_target = os.path.abspath(os.path.join(base_dir, target_path))   
        if not abs_target.startswith(abs_base):
            raise SecurityError(f"Path traversal blocked: {target_path}")
        return abs_target


# Quick test
if __name__ == "__main__":
    sanitizer = PathSanitizer()

    # Should succeed
    try:
        safe = sanitizer.validate_safe_path("./workspace", "reports/q1.txt")
        print(f"Safe path: {safe}")
    except SecurityError as e:
        print(f"ERROR: {e}")

    # Should fail — directory traversal attempt
    try:
        unsafe = sanitizer.validate_safe_path("./workspace", "../../etc/passwd")
        print(f"UNSAFE path allowed (BUG!): {unsafe}")
    except SecurityError as e:
        print(f"Blocked (correct!): {e}")
