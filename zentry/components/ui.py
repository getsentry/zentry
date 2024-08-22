from fasthtml.common import *
from utils import fmt_percentage_signed


SQL_KEYWORDS = [
    "AND",
    "DELETE",
    "FROM",
    "LIMIT",
    "OR",
    "ORDER BY",
    "SELECT",
    "SET",
    "UPDATE",
    "WHERE",
]


def no_data(header):
    return Div(
        header,
        Div(
            Div("No data available.", cls="no-data-msg"),
            cls="body",
        ),
        cls="card",
    )


def loading_placeholder(header, route):
    return Div(
        header,
        Div(
            Div("One moment please, loading data...", cls="loading-msg"),
            cls="body",
        ),
        hx_get=route,
        hx_trigger="load",
        hx_swap="outerHTML",
        cls="card",
    )


def metric(title, id, value, value_prev, score, formatter=lambda x: x):
    """
    The card representing one metric.
    """
    change = (value_prev - value) / value_prev

    return Div(
        Div(title, cls="header"),
        Div(formatter(value), cls="value"),
        Div(
            fmt_percentage_signed(change),
            title="Change compared to the last time period",
            cls=f'change {"up" if change >=0 else "down"}',
        ),
        Div(score, cls=f"score {score.lower()}"),
        id=id,
        cls="metric",
    )


def metric_simple(id, value, formatter=lambda x: x, cls="row"):
    """
    The card representing one metric in the databases list.
    """
    return Div(
        Div(formatter(value), cls="value"),
        id=id,
        cls=cls,
    )


def query(query, id, cls="row query"):
    """
    Format the query in Markdown and then render the markdown.
    This is why we need MarkdownJS in fast_app()
    """
    for keyword in SQL_KEYWORDS:
        query = query.replace(keyword, f"**{keyword}**")

    return Div(
        Div(query, cls="marked"),
        id=id,
        cls=cls,
    )


def header():
    return Div(
        Img(src="/assets/img/zentry-logo.svg", alt="Zentry logo", cls="logo"),
        Div("Zentry", cls="title"),
        cls="header",
    )


def footer():
    return Div(
        P(
            "Built by",
            A("Anton Pirker", href="https://github.com/antonpirker", target="_blank"),
            " during Sentry Hackweek 2024. ",
            A(
                "Source code",
                href="https://github.com/getsentry/zentry",
                target="_blank",
            ),
            style="margin-bottom: 2em;",
        ),
        A(
            Img(src="/assets/img/sentry.png", alt="Sentry logo", cls="sentry-logo"),
            href="https://sentry.io",
            target="_blank",
        ),
        cls="footer",
    )
