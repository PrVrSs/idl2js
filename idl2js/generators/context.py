from contextvars import ContextVar


_generation_context = ContextVar('generation_context', default=None)


def get_coverage():
    ctx = _generation_context.get()
    if ctx is None:
        return None
    return ctx.get('coverage')


def set_context(ctx):
    return _generation_context.set(ctx)


def clear_context():
    _generation_context.set(None)
