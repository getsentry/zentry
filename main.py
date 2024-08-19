import os

from fasthtml.common import *

import sentry_sdk


sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    traces_sample_rate=1.0,
    debug=True,
)

app,rt = fast_app()


def header(title):
    return Div(
        Li(A("Issues", href="/"), A("State of the System", href="/state")), 
        Titled(title),
        id="header",
    )


@app.get('/state')
def state(): 
    return Title("Zentry"), Div(
        header("State of the System"),
        id="main",
    )


@app.get('/')
def home(): 
    return Title("Zentry"), Div(
        header("Issues"),
        id="main",
    )

serve()