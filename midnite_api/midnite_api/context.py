from contextvars import ContextVar


request_id_ctx_var: ContextVar[str] = ContextVar("request_id", default=None)

def get_request_id() -> str:
    return request_id_ctx_var.get()
