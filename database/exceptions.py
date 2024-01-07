from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class StandardException(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message


def setup_custom_errors(app: FastAPI):
    @app.exception_handler(StandardException)
    async def standard_exception_handler(request: Request, exc: StandardException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "message": exc.message
            }
        )
