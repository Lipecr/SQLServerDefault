from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers.router_ import router_
from .utils.utils import (
    startup, shutdown, 
    validation_exception_handler, 
    RequestValidationError
)

def create_sync_server() -> FastAPI:
    """
    Cria e retorna a instância do aplicativo FastAPI.
    """
    app = FastAPI(
        title="",
        description="",
    )

    app.add_event_handler("startup", startup)
    app.add_event_handler("shutdown", shutdown)
    # Adiciona manipulador de exceções para erros de validação
    app.add_exception_handler(RequestValidationError, validation_exception_handler)

    # Configuração de middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Registrar rotas
    app.include_router(router_)

    return app
