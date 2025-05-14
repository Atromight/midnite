import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from midnite_api.context import request_id_ctx_var


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request_id_ctx_var.set(request_id)
        return await call_next(request)
