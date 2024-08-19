import os

from fasthtml.common import *

import sentry_api
import sentry_sdk

from components import backend_state, cache_state, database_state, frontend_state, queue_state

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    traces_sample_rate=1.0,
    debug=True,
)

app, rt = fast_app()


def header(title):
    return Div(
        Li(A("Issues", href="/"), A("State of the System", href="/state")),
        Titled(title),
        id="header",
    )


@app.get("/state")
def state():
    frontend_data = sentry_api.get_frontend_state(
        project_id=os.environ.get("SENTRY_FRONTEND_PROJECT_ID"),
        environment=os.environ.get("SENTRY_FRONTEND_ENVIRONMENT"),
    )

    backend_data = sentry_api.get_backend_state(
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
        header("State of the System"),
        frontend_state(frontend_data),
        backend_state(backend_data),
        cache_state(cache_data),
        queue_state(queue_data),
        database_state(database_data),
        id="main",
    )


@app.get("/")
def home():
    return Title("Zentry"), Div(
        header("Issues"),
        id="main",
    )


serve()
