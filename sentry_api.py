import os

import requests


SENTRY_API_BASE_URL = os.environ.get("SENTRY_API_BASE_URL", "https://sentry.io/api/0")

SENTRY_API_AUTH_TOKEN = os.environ.get("SENTRY_API_AUTH_TOKEN")
if not SENTRY_API_AUTH_TOKEN:
    raise ValueError("Please set the SENTRY_API_AUTH_TOKEN environment variable")

STATS_PERIOD = os.environ.get("STATS_PERIOD", "1h")
REFERRER = os.environ.get("REFERRER", "zentry")


def _make_api_request(path, params={}):
    url = SENTRY_API_BASE_URL + path
    headers = {"Authorization": f"Bearer {SENTRY_API_AUTH_TOKEN}"}

    base_params = {
        "statsPeriod": STATS_PERIOD,
        "referrer": REFERRER,
    }
    combined_params = {}
    combined_params.update(base_params)
    combined_params.update(params)

    response = requests.get(
        url,
        headers=headers,
        params=combined_params,
    )

    return response.json()


def get_frontend_state(project_id, environment):
    response = _make_api_request(
        path=f"/organizations/sentry/events/",
        params={
            "project": project_id,
            "environment": environment,
            "dataset": "metrics",
            "query": 'transaction.op:[pageload,""] span.op:[ui.interaction.click,ui.interaction.hover,ui.interaction.drag,ui.interaction.press,""] !transaction:"<< unparameterized >>"',
            "field": [
                "p75(measurements.ttfb)",
                "p75(measurements.fcp)",
                "p75(measurements.inp)",
                "performance_score(measurements.score.ttfb)",
                "performance_score(measurements.score.fcp)",
                "performance_score(measurements.score.inp)",
            ],
        },
    )

    if len(response["data"]) == 0:
        return None

    # Rename returned keys for better readability
    rename_keys = {
        "p75(measurements.ttfb)": "ttfb",
        "p75(measurements.fcp)": "fcp",
        "p75(measurements.inp)": "inp",
        "performance_score(measurements.score.ttfb)": "ttfb_score",
        "performance_score(measurements.score.fcp)": "fcp_score",
        "performance_score(measurements.score.inp)": "inp_score",
    }

    data = response["data"][0]
    clean_data = {}

    for key in data.keys():
        if key in rename_keys:
            clean_data[rename_keys[key]] = data[key]

    return clean_data


def get_backend_state(project_id, environment):
    response = _make_api_request(
        path=f"/organizations/sentry/events/",
        params={
            "project": project_id,
            "environment": environment,
            "dataset": "metrics",
            "query": "event.type:transaction",
            "field": [
                "failure_rate()",
                "apdex()",
            ],
        },
    )

    if len(response["data"]) == 0:
        return None

    # Rename returned keys for better readability
    rename_keys = {
        "failure_rate()": "failure_rate",
        "apdex()": "apdex",
    }

    data = response["data"][0]
    clean_data = {}

    for key in data.keys():
        if key in rename_keys:
            clean_data[rename_keys[key]] = data[key]

    return clean_data


def get_cache_state(project_id, environment):
    response = _make_api_request(
        path=f"/organizations/sentry/events/",
        params={
            "project": project_id,
            "environment": environment,
            "dataset": "spansMetrics",
            "per_page": 5,
            "query": "span.op:[cache.get_item,cache.get]",
            "field": [
                "project", 
                "project.id",
                "transaction", 
                "cache_miss_rate()",
                "sum(span.self_time)", 
                "avg(cache.item_size)",
                "time_spent_percentage()",
            ],
            "sort": "-time_spent_percentage()",
        },
    )

    if len(response["data"]) == 0:
        return None

    # Rename returned keys for better readability
    rename_keys = {
        "avg_if(span.duration,span.op,queue.process)": "processing_time_avg",
        "avg(messaging.message.receive.latency)": "time_in_queue_avg",
        "trace_status_rate(ok)": "success_rate",
        "time_spent_percentage(app,span.duration)": "time_percentage",
    }

    data = response["data"][0]  
    clean_data = {}

    for key in data.keys():
        if key in rename_keys:
            clean_data[rename_keys[key]] = data[key]

    return clean_data


def get_queue_state(project_id, environment):
    response = _make_api_request(
        path=f"/organizations/sentry/events/",
        params={
            "project": project_id,
            "environment": environment,
            "dataset": "spansMetrics",
            "per_page": 5,
            "query": "span.op:[queue.process,queue.publish]",
            "field": [
                "avg_if(span.duration,span.op,queue.process)", 
                "avg(messaging.message.receive.latency)",
                "trace_status_rate(ok)",
                "time_spent_percentage(app,span.duration)",
            ],
            "sort": "-time_spent_percentage(app,span.duration)",
        },
    )

    if len(response["data"]) == 0:
        return None

    # Rename returned keys for better readability
    rename_keys = {
        "avg_if(span.duration,span.op,queue.process)": "processing_time_avg",
        "avg(messaging.message.receive.latency)": "time_in_queue_avg",
        "trace_status_rate(ok)": "success_rate",
        "time_spent_percentage(app,span.duration)": "time_percentage",
    }

    data = response["data"][0]
    clean_data = {}

    for key in data.keys():
        if key in rename_keys:
            clean_data[rename_keys[key]] = data[key]

    return clean_data


def get_database_state(project_id, environment):
    response = _make_api_request(
        path=f"/organizations/sentry/events/",
        params={
            "project": project_id,
            "environment": environment,
            "dataset": "spansMetrics",
            "per_page": 5,
            "query": "span.module:db has:span.description",
            "field": [
                "span.description",
                "avg(span.self_time)",
                "sum(span.self_time)",
                "time_spent_percentage()",
            ],
            "sort": "-time_spent_percentage()",
        },
    )

    if len(response["data"]) == 0:
        return None

    # Rename returned keys for better readability
    data = response["data"]
    clean_data = []

    for item in data:
        clean_data.append({
            "query": item["span.description"],
            "time_avg": item["avg(span.self_time)"],
            "time_total": item["sum(span.self_time)"],
            "time_percentage": item["time_spent_percentage()"],
        })

    return clean_data
