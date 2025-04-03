async def callWithNonNoneArgs(f, *args, **kwargs):
    """
    Calls a function, passing through only those keyword arguments that are not None.
    """
    kwargsNotNone = {k: v for k, v in kwargs.items() if v is not None}
    return f(*args, **kwargsNotNone)