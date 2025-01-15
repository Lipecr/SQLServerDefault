import uvicorn
from app import create_sync_server  # Certifique-se de que esta função retorna um app FastAPI

app = create_sync_server()

if __name__ == "__main__":
    uvicorn.run(
        app="main:app",  # Referência ao app importado neste arquivo
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True,  # Somente para desenvolvimento
    )
