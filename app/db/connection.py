from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy import text
from ..config.config_db import ConfigSQLServer

class SQLServerConn:
    """
    Gerenciador de conexão com o banco de dados SQL Server.
    
    Esta classe implementa as práticas recomendadas do SQLAlchemy 2.0 para
    gerenciamento de conexões assíncronas com o SQL Server.
    """
    
    def __init__(
        self,
        pool_size: int = 5,
        max_overflow: int = 10,
        pool_recycle: int = 3600,
        pool_timeout: int = 30
    ):
        """
        Inicializa o gerenciador de conexão.

        Args:
            pool_size (int): Tamanho do pool de conexões. Padrão: 5
            max_overflow (int): Número máximo de conexões extras permitidas. Padrão: 10
            pool_recycle (int): Tempo em segundos para reciclar conexões. Padrão: 3600 (1 hora)
            pool_timeout (int): Tempo máximo de espera por uma conexão do pool. Padrão: 30 segundos
        """
        self.config = ConfigSQLServer()
        self.engine = create_async_engine(
            self.config.DATABASE_URL,
            echo=False,
            pool_pre_ping=True,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_recycle=pool_recycle,
            pool_timeout=pool_timeout
        )
        
        # Usando async_sessionmaker em vez de sessionmaker
        self.async_session_maker = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False
        )

    async def test_connection(self) -> bool:
        """
        Testa a conectividade com o banco de dados.

        Returns:
            bool: True se a conexão for bem-sucedida, False caso contrário.
        """
        try:
            async with self.engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
                await conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao conectar ao banco de dados: {str(e)}")
            return False

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Gerenciador de contexto para sessões do banco de dados.
        
        Yields:
            AsyncSession: Sessão assíncrona do SQLAlchemy.
        
        Example:
            async with conn.get_session() as session:
                result = await session.execute(text("SELECT * FROM tabela"))
                await session.commit()
        """
        session: AsyncSession = self.async_session_maker()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def get_db(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Gerador de dependência para injeção de sessões no FastAPI.
        
        Yields:
            AsyncSession: Sessão assíncrona do SQLAlchemy.
        
        Example:
            @app.get("/items")
            async def get_items(db: AsyncSession = Depends(conn.get_db)):
                result = await db.execute(text("SELECT * FROM items"))
                return result.scalars().all()
        """
        async with self.get_session() as session:
            yield session

    async def dispose(self) -> None:
        """
        Finaliza todas as conexões do pool.
        Este método deve ser chamado ao encerrar a aplicação.
        """
        await self.engine.dispose()

# Instância global para uso em toda a aplicação
conn = SQLServerConn()