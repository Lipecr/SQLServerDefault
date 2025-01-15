from typing import List, Optional, Any, Dict
from fastapi.responses import JSONResponse
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from .db.connection import conn
from ..config.config_fields import ConfigFields
import json

# Wrappers para métodos assíncronos
async def startup():
    if not await conn.test_connection():
        raise RuntimeError("Falha ao conectar ao banco de dados")

async def shutdown():
    await conn.dispose()

def create_json_response(
    codigo: int,
    mensagem: str,
    dados: Optional[List[Dict[str, Any]]] = None,
    headers: Optional[Dict[str, str]] = None,
) -> JSONResponse:
    """
    Gera uma resposta JSON padronizada usando JSONResponse do FastAPI.

    Args:
        codigo (int): Código de status HTTP (200, 404, etc.).
        mensagem (str): Mensagem descritiva da operação.
        dados (Optional[List[Dict[str, Any]]]): Lista com os dados da resposta.
        headers (Optional[Dict[str, str]]): Cabeçalhos adicionais para a resposta.

    Returns:
        JSONResponse: Resposta JSON padronizada.
    """
    return JSONResponse(
        status_code=codigo,
        content={
            "codigo": codigo,
            "mensagem": mensagem,
            "dados": dados or [],
        },
        headers=headers or {}
    )

def extract_data_from_response(response: JSONResponse) -> dict:
    """
    Extrai e retorna os dados do JSONResponse.

    Args:
        response (JSONResponse): Objeto JSONResponse retornado por uma função FastAPI.

    Returns:
        dict: Dados contidos no JSONResponse.
    """
    try:
        content = response.body.decode()  # Decodifica o conteúdo do body
        return json.loads(content)  # Converte para um objeto Python
    except AttributeError as e:
        raise ValueError(f"Erro ao acessar o conteúdo do JSONResponse: {str(e)}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Erro ao decodificar JSONResponse: {str(e)}")
    

# Manipulador de exceção para validação de requisição
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Manipula exceções de validação Pydantic em requisições.
    
    Args:
        request (Request): O objeto da requisição.
        exc (RequestValidationError): A exceção de validação.

    Returns:
        JSONResponse: Resposta JSON formatada com os detalhes do erro.
    """
    errors = [
        {
            "campo": err["loc"][-1] if isinstance(err["loc"][-1], str) else "",  # Pega o último elemento que deve ser o nome do campo
            "erro": ConfigFields.FIELD_VALIDATE_PYDANTIC.get(err["msg"].lower(), err["msg"]).format(**err.get("ctx", {}))
        }
        for err in exc.errors()
    ]
    
    return create_json_response(
        status_code=422,
        mensagem="erro",
        dados=errors
    )
