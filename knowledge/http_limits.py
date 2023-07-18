from starlette.responses import JSONResponse


class BodyLimit:
    """Bound ASGI request buffering before multipart/JSON parsers allocate objects."""

    def __init__(self, app, limit=2100000):
        self.app = app
        self.limit = limit

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        headers = dict(scope.get("headers", []))
        try:
            declared = int(headers.get(b"content-length", b"0"))
        except ValueError:
            declared = self.limit + 1
        if declared > self.limit:
            return await JSONResponse({"detail": "Request exceeds upload limit"}, 413)(
                scope, receive, send
            )
        messages = []
        total = 0
        while True:
            message = await receive()
            messages.append(message)
            if message["type"] == "http.disconnect":
                break
            total += len(message.get("body", b""))
            if total > self.limit:
                return await JSONResponse(
                    {"detail": "Request exceeds upload limit"}, 413
                )(scope, receive, send)
            if not message.get("more_body", False):
                break

        async def replay():
            if messages:
                return messages.pop(0)
            return await receive()

        await self.app(scope, replay, send)
