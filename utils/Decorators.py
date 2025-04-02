def subcommand(parent: str, name: str = None):
    """
    Decorator to mark a function as a subcommand of a parent group.
    """
    def decorator(func):
        func._parent_group = parent  # Attach parent group metadata
        func._subcommand_name = name or func.__name__  # Define explicit name for the subcommand
        func._is_subcommand = True  # Mark as subcommand
        return func
    return decorator
