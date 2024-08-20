from fasthtml.common import *

from utils import fmt_duration, fmt_percentage, fmt_percentage_signed, fmt_round_2


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
    "UPDATE", 
    "WHERE", 
]


def metric(title, id, value, value_prev, score, formatter=lambda x: x):
    """
    The card representing one metric.
    """
    change = (value_prev - value) / value_prev

    return Div(
        Div(title, cls='header'),
        Div(formatter(value), cls='value'),
        Div(fmt_percentage_signed(change), cls=f'change {"up" if change >=0 else "down"}'),
        Div(score, cls='score meh'),
        id=id,
        cls="metric",
    )


def metric_simple(id, value, formatter=lambda x: x, cls="row"):
    """
    The card representing one metric in the databases list.
    """
    return Div(
        Div(formatter(value), cls='value'),
        id=id,
        cls=cls,
    )


def query(query, id, cls="row query"):
    # TODO: highlight SQL keywords
    # for keyword in SQL_KEYWORDS:
    #     query = query.replace(keyword, f"<b>{keyword}</b>")

    return Div(
        # Div(show(html2ft(query)), cls='value'),
        Div(query),
        id=id,
        cls=cls,
    )


async def frontend_state(data=None, data_prev=None):
    if not data:
        return Div(
            H2("Frotend"),
            Div(
                P("No data available"),
                cls="body",
            ),
            cls="card",
        )

    return Div(
        H2("Frontend"),
        Div(
            metric(
                title="Time to First Byte",
                id="ttfb",
                value=data["ttfb"],
                value_prev=data_prev["ttfb"],
                score="TODO",
                formatter=fmt_duration,
            ),
            metric(
                title="First Contentful Paint",
                id="fcp",
                value=data["fcp"],
                value_prev=data_prev["fcp"],
                score="TODO",
                formatter=fmt_duration,
            ),
            metric(
                title="Interaction to Next Paint",
                id="inp",
                value=data["inp"],
                value_prev=data_prev["inp"],
                score="TODO",
            ),
            cls="body",
        ),
        id="frontend",
        cls="card",
    )


async def backend_state(data=None, data_prev=None):
    if not data:
        return Div(
            H2("Backend"),
            Div(
                P("No data available"),
                cls="body",
            ),
            cls="card",
        )

    return Div(
        H2("Backend"),
        Div(
            metric(
                title="Failure Rate",
                id="failure-rate",
                value=data["failure_rate"],
                value_prev=data_prev["failure_rate"],
                score="TODO",
                formatter=fmt_percentage,
            ),
            metric(
                title="Apdex",
                id="apdex",
                value=data["apdex"],
                value_prev=data_prev["apdex"],
                score="TODO",
                formatter=fmt_round_2,
            ),
            cls="body",
        ),
        id="backend",
        cls="card",
    )


async def requests_state(title, id, data=None, data_prev=None):
    if not data:
        return Div(
            H2(title),
            Div(
                P("No data available"),
                cls="body",
            ),
            cls="card",
        )
    
    failure_rate = (
        data["response_rate_3xx"]
        + data["response_rate_4xx"]
        + data["response_rate_5xx"]
    )

    failure_rate_prev = (
        data_prev["response_rate_3xx"]
        + data_prev["response_rate_4xx"]
        + data_prev["response_rate_5xx"]
    )

    return Div(
        H2(title),
        Div(
            metric(
                title="Failure Rate",
                id="time_avg",
                value=failure_rate,
                value_prev=failure_rate_prev,
                score="TODO",
                formatter=fmt_percentage,
            ),
            metric(
                title="Avg Duration",
                id="time_avg",
                value=data["time_avg"],
                value_prev=data_prev["time_avg"],
                score="TODO",
                formatter=fmt_duration,
            ),
            cls="body",
        ),
        id=id,
        cls="card",
    )


async def frontend_requests_state(data=None, data_prev=None):
    return await requests_state(
        "Outbound HTTP Requests",
        "frontend-outbound-requests",
        data,
        data_prev,
    )


async def backend_requests_state(data=None, data_prev=None):
    return await requests_state(
        "Outbound HTTP Requests",
        "backend-outbound-requests",
        data,
        data_prev,
    )


async def cache_state(data=None, data_prev=None):
    if not data:
        return Div(
            H2("Caches"),
            Div(
                P("No data available"),
                cls="body",
            ),
            cls="card",
        )

    return Div(
        H2("Caches"),
        metric(
            title="Cache hit rate",
            id="cahe_hit_rate",
            value=1 - data["miss_rate"],
            value_prev=1 - data_prev["miss_rate"],
            score="TODO",
            formatter=fmt_percentage,
        ),
        id="cache",
    )


async def queue_state(data=None, data_prev=None):
    if not data:
        return Div(
            H2("Queues"),
            Div(
                P("No data available"),
                cls="body",
            ),
            cls="card",
        )

    return Div(
        H2("Queues"),
        Div(
            # TODO: if we add this, the UI looks ugly, so disabling for now
            # metric(
            #     title="Failure Rate",
            #     id="queue_failure_rate",
            #     value=1 - data["success_rate"],
            #     value_prev=1 - data_prev["success_rate"],
            #     score="TODO",
            #     formatter=fmt_percentage,
            # ),
            metric(
                title="Avg Processing Time",
                id="processing_time_avg",
                value=data["processing_time_avg"],
                value_prev=data_prev["processing_time_avg"],
                score="TODO",
                formatter=fmt_duration,
            ),
            metric(
                title="Avg Time in Queue",
                id="time_in_queue_avg",
                value=data["time_in_queue_avg"],
                value_prev=data_prev["time_in_queue_avg"],
                score="TODO",
                formatter=fmt_duration,
            ),
            cls="body",
        ),
        id="queue",
        cls="card",
    )


async def database_state(data=None, data_prev=None):
    output = []
    for item in data:
        output += [
            query(
                item["query"], 
                id="query",
                cls="row query",
            ),
            metric_simple(
                value=item["time_avg"], 
                id="time_avg", 
                formatter=fmt_duration,
                cls="row right",
            ),
            metric_simple(
                value=item["time_total"], 
                id="time_total", 
                formatter=fmt_duration,
                cls="row right",
            ),
            
        ]

    return Div(
        H2("Database"),
        Div(
            Div(
                # Headline
                Div("Query", cls="row-header"),
                Div("Avg Duration", cls="row-header right"),
                Div("Time Spent", cls="row-header right"),
                # Queries
                *output,
                cls="grid-card-list"
            ),
            cls="body",
        ),
        id="database",
        cls="card",
        style="min-height: 400px; height: unset;",
    )
