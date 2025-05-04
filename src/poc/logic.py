def plan(task: str) -> str:
    """Plan the given task and return the plan"""
    # For now just return a simple response, but this could call LLM later
    return f"Plan for: {task}\n1. Analyze requirements\n2. Design solution\n3. Implement code\n4. Test changes"
