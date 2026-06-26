from fastapi import FastAPI

from app.api.routes import router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Audit-Ready Finance Agent",
        version="0.1.0",
        description="A typed FastAPI foundation for finance-agent workflows.",
    )
    app.include_router(router)
    return app


app = create_app()
