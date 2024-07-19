import os
from sanic import Request, text
from app import app

app.update_config({
    "PORT": 8000,
    "HOST": os.getenv("SANIC_HOST", "0.0.0.0"),
    "DEBUG": bool(os.getenv("SANIC_DEBUG", True))
})


@app.get("/")
async def index_page(request: Request):
    return text("Hello world!")


if __name__ == "__main__":
    app.run(
        host=app.config.HOST,
        port=app.config.PORT,
        debug=app.config.DEBUG
    )
