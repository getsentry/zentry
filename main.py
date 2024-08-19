import os

from fasthtml.common import *

import sentry_api
import sentry_sdk

from components import (
    backend_requests_state,
    backend_state,
    cache_state,
    database_state,
    frontend_requests_state,
    frontend_state,
    queue_state,
)

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    traces_sample_rate=1.0,
    # debug=True,
)

app, rt = fast_app()


async def header(title):
    return Div(
        Li(A("Issues", href="/"), A("State of the System", href="/state")),
        Titled(title),
        id="header",
    )


@app.get("/state")
async def state():
    frontend_data = sentry_api.get_frontend_state(
        project_id=os.environ.get("SENTRY_FRONTEND_PROJECT_ID"),
        environment=os.environ.get("SENTRY_FRONTEND_ENVIRONMENT"),
    )

    frontent_requests_data = sentry_api.get_requests_state(
        project_id=os.environ.get("SENTRY_FRONTEND_PROJECT_ID"),
        environment=os.environ.get("SENTRY_FRONTEND_ENVIRONMENT"),
    )

    backend_data = sentry_api.get_backend_state(
        project_id=os.environ.get("SENTRY_BACKEND_PROJECT_ID"),
        environment=os.environ.get("SENTRY_BACKEND_ENVIRONMENT"),
    )

    backend_requests_data = sentry_api.get_requests_state(
        project_id=os.environ.get("SENTRY_BACKEND_PROJECT_ID"),
        environment=os.environ.get("SENTRY_BACKEND_ENVIRONMENT"),
    )

    cache_data = sentry_api.get_cache_state(
        project_id=os.environ.get("SENTRY_BACKEND_PROJECT_ID"),
        environment=os.environ.get("SENTRY_BACKEND_ENVIRONMENT"),
    )

    queue_data = sentry_api.get_queue_state(
        project_id=os.environ.get("SENTRY_BACKEND_PROJECT_ID"),
        environment=os.environ.get("SENTRY_BACKEND_ENVIRONMENT"),
    )

    database_data = sentry_api.get_database_state(
        project_id=os.environ.get("SENTRY_BACKEND_PROJECT_ID"),
        environment=os.environ.get("SENTRY_BACKEND_ENVIRONMENT"),
    )

    return Title("Zentry"), Div(
        await header("State of the System"),
        await frontend_state(frontend_data),
        await frontend_requests_state(frontent_requests_data),
        await backend_state(backend_data),
        await backend_requests_state(backend_requests_data),
        await cache_state(cache_data),
        await queue_state(queue_data),
        await database_state(database_data),
        id="main",
    )


@app.get("/")
async def home():
    return Title("Zentry"), Div(
        header("Issues"),
        id="main",
    )


serve()
