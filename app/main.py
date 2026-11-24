"""
    uvicorn app.main:app --reload
"""

import logging
import time

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request, Response, status

from app.config import Settings, get_settings
from app.models import HealthResponse, Note, NoteCreate, NoteUpdate
from app.storage import NoteStorage

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("notes-api")


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    storage = NoteStorage(settings.database_path)

    app = FastAPI(title=settings.app_name, version=settings.app_version)
    app.state.settings = settings
    app.state.storage = storage
    app.state.started_at = time.time()
    app.state.request_count = 0

    # ---------- middleware ----------

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        app.state.request_count += 1
        logger.info("%s %s -> %s (%.1f ms)", request.method, request.url.path, response.status_code, duration_ms)
        return response

    # ---------- dependencies ----------

    def get_storage() -> NoteStorage:
        return app.state.storage

    def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
        expected = app.state.settings.api_key
        if expected and x_api_key != expected:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing API key")

    # ---------- service endpoints ----------

    @app.get("/", tags=["service"])
    def root() -> dict:
        return {"name": settings.app_name, "version": settings.app_version, "docs": "/docs"}

    @app.get("/health", response_model=HealthResponse, tags=["service"])
    def health(response: Response, store: NoteStorage = Depends(get_storage)) -> HealthResponse:
        db_ok = store.ping()
        if not db_ok:
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return HealthResponse(
            status="ok" if db_ok else "degraded",
            version=settings.app_version,
            environment=settings.app_env,
            database="ok" if db_ok else "unavailable",
        )

    @app.get("/metrics", tags=["service"])
    def metrics() -> dict:
        return {
            "uptime_seconds": round(time.time() - app.state.started_at, 1),
            "requests_total": app.state.request_count,
        }

    # ---------- notes CRUD ----------

    @app.get("/notes", response_model=list[Note], tags=["notes"])
    def list_notes(
        search: str | None = Query(default=None, max_length=100),
        limit: int = Query(default=50, ge=1, le=100),
        offset: int = Query(default=0, ge=0),
        store: NoteStorage = Depends(get_storage),
    ) -> list[Note]:
        return store.list(search=search, limit=limit, offset=offset)

    @app.get("/notes/{note_id}", response_model=Note, tags=["notes"])
    def get_note(note_id: int, store: NoteStorage = Depends(get_storage)) -> Note:
        note = store.get(note_id)
        if note is None:
            raise HTTPException(status_code=404, detail="Note not found")
        return note

    @app.post(
        "/notes",
        response_model=Note,
        status_code=status.HTTP_201_CREATED,
        dependencies=[Depends(require_api_key)],
        tags=["notes"],
    )
    def create_note(data: NoteCreate, store: NoteStorage = Depends(get_storage)) -> Note:
        return store.create(data)

    @app.put("/notes/{note_id}", response_model=Note, dependencies=[Depends(require_api_key)], tags=["notes"])
    def update_note(note_id: int, data: NoteUpdate, store: NoteStorage = Depends(get_storage)) -> Note:
        note = store.update(note_id, data)
        if note is None:
            raise HTTPException(status_code=404, detail="Note not found")
        return note

    @app.delete(
        "/notes/{note_id}",
        status_code=status.HTTP_204_NO_CONTENT,
        dependencies=[Depends(require_api_key)],
        tags=["notes"],
    )
    def delete_note(note_id: int, store: NoteStorage = Depends(get_storage)) -> Response:
        if not store.delete(note_id):
            raise HTTPException(status_code=404, detail="Note not found")
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return app


app = create_app()
