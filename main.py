import os

from fasthtml.common import *

import sentry_api
import sentry_sdk


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


def frontend_state(data=None):
    return Div(
        H2("Frontend"),
        P("Web Server Responsiveness (Time to first byte): ", data["ttfb"]),
        P(
            "Time the first content takes to render (First Contentful Paint): ",
            data["fcp"],
        ),
        P("Responsiveness (Interaction to Next Paint): ", data["inp"]),
    )


def backend_state(data=None):
    return Div(
        H2("Backend"),
        P("Failure Rate: ", data["failure_rate"]),
        P("Apdex: ", data["apdex"]),
    )


def cache_state(data=None):
    return Div(
        H2("Cache"),
        P("not available"),
    )


def queue_state(data=None):
    return Div(
        H2("Queues"),
        P("Average processing time: ", data["processing_time_avg"]),
        P("Average time in queue: ", data["time_in_queue_avg"]),
        P("Failure Rate: ", 1-data["success_rate"]),
    )


def database_state(data=None):
    output = []
    for item in data:
        output.append(
            Div(
                P("Query:", item["query"]),
                P("Time avg:", item["time_avg"]),
                P("Time total::", item["time_total"]),
                P("Time percentage:", item["time_percentage"]),
            )
        )

    return Div(
        H2("Database"),
        *output,
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
