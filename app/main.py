from fastapi import FastAPI

from app.routers import knowhows, major_categories, middle_categories

app = FastAPI(title="Knowhow API", version="0.1.0")

app.include_router(major_categories.router)
app.include_router(middle_categories.router)
app.include_router(knowhows.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
