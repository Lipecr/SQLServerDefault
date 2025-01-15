# router_.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..db.connection import conn
from ..utils.utils import create_json_response
from ..controllers.controller_ import controller_
import logging
from ..schemas.schema_ import Schema

logger = logging.getLogger(__name__)

router_ = APIRouter(
    prefix="/router",
    tags=["Router"],
    responses={404: {"": ""}},
)

@router_.post("/", status_code=200)
async def login(data: Schema, db: AsyncSession = Depends(conn.get_db)):
    try:
        return await controller_(db, data)
    except Exception as e:
        logger.exception(f"Erro")
        return create_json_response(
            codigo=500,
            mensagem=f"Erro: {str(e)}"
        )


