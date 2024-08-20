import datetime
import os

SENTRY_API_BASE_URL = os.environ.get("SENTRY_API_BASE_URL", "https://sentry.io/api/0")

SENTRY_API_AUTH_TOKEN = os.environ.get("SENTRY_API_AUTH_TOKEN")
if not SENTRY_API_AUTH_TOKEN:
    raise ValueError("Please set the SENTRY_API_AUTH_TOKEN environment variable")

REFERRER = os.environ.get("REFERRER", "zentry")
TIME_PERIOD_IN_DAYS = 1

client = None


def _get_time_period(preview_time_period):
    # We assume "now" is the end of the day today
    # Makes it way easier to cache results of the API calls
    now = datetime.datetime.now(datetime.timezone.utc)
    now = now.replace(hour=0, minute=0, second=0, microsecond=0)
    now += datetime.timedelta(days=1, microseconds=-1)

    if preview_time_period:
        start = now - datetime.timedelta(days=2 * TIME_PERIOD_IN_DAYS)
        end = now - datetime.timedelta(days=TIME_PERIOD_IN_DAYS)
    else:
        start = now - datetime.timedelta(days=TIME_PERIOD_IN_DAYS)
        end = now

    return (start, end)


async def _make_api_request(path, params={}, preview_time_period=False):
    url = SENTRY_API_BASE_URL + path
    headers = {"Authorization": f"Bearer {SENTRY_API_AUTH_TOKEN}"}

    start, end = _get_time_period(preview_time_period)

    base_params = {
        "referrer": REFERRER,
        "start": start.isoformat(),
        "end": end.isoformat(),
    }
    combined_params = {}
    combined_params.update(base_params)
    combined_params.update(params)

    async with client.get(url, headers=headers, params=combined_params) as response:
        return await response.json()


async def get_frontend_state(project_id, environment, preview_time_period=False):
    response = await _make_api_request(
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
        preview_time_period=preview_time_period,
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


async def get_backend_state(project_id, environment, preview_time_period=False):
    response = await _make_api_request(
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
        preview_time_period=preview_time_period,
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


async def get_requests_state(project_id, environment, preview_time_period=False):
    response = await _make_api_request(
        path=f"/organizations/sentry/events/",
        params={
            "project": project_id,
            "environment": environment,
            "dataset": "spansMetrics",
            "query": "span.module:http span.op:http.client",
            "field": [
                "http_response_rate(3)",
                "http_response_rate(4)",
                "http_response_rate(5)",
                "avg(span.self_time)",
            ],
        },
        preview_time_period=preview_time_period,
    )

    if len(response["data"]) == 0:
        return None

    # Rename returned keys for better readability
    rename_keys = {
        "http_response_rate(3)": "response_rate_3xx",
        "http_response_rate(4)": "response_rate_4xx",
        "http_response_rate(5)": "response_rate_5xx",
        "avg(span.self_time)": "time_avg",
    }

    data = response["data"][0]
    clean_data = {}

    for key in data.keys():
        if key in rename_keys:
            clean_data[rename_keys[key]] = data[key]

    return clean_data


async def get_cache_state(project_id, environment, preview_time_period=False):
    response = await _make_api_request(
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
        preview_time_period=preview_time_period,
    )

    if len(response["data"]) == 0:
        return None

    # Rename returned keys for better readability
    rename_keys = {
        "cache_miss_rate()": "miss_rate",
        "sum(span.self_time)": "time_total",
        "avg(cache.item_size)": "time_avg",
    }

    data = response["data"][0]
    clean_data = {}

    for key in data.keys():
        if key in rename_keys:
            clean_data[rename_keys[key]] = data[key]

    return clean_data


async def get_queue_state(project_id, environment, preview_time_period=False):
    response = await _make_api_request(
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
        preview_time_period=preview_time_period,
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


async def get_database_state(project_id, environment, preview_time_period=False):
    response = await _make_api_request(
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
        preview_time_period=preview_time_period,
    )

    if len(response["data"]) == 0:
        return None

    # Rename returned keys for better readability
    data = response["data"]
    clean_data = []

    for item in data:
        clean_data.append(
            {
                "query": item["span.description"],
                "time_avg": item["avg(span.self_time)"],
                "time_total": item["sum(span.self_time)"],
                "time_percentage": item["time_spent_percentage()"],
            }
        )

    return clean_data


async def get_data():
    frontend_id = os.environ.get("SENTRY_FRONTEND_PROJECT_ID")
    frontend_env = os.environ.get("SENTRY_FRONTEND_ENVIRONMENT")
    backend_id = os.environ.get("SENTRY_BACKEND_PROJECT_ID")
    backend_env = os.environ.get("SENTRY_BACKEND_ENVIRONMENT")

    data = {}

    data["frontend"] = await get_frontend_state(
        project_id=frontend_id,
        environment=frontend_env,
    )
    data["frontend_prev"] = await get_frontend_state(
        project_id=frontend_id,
        environment=frontend_env,
        preview_time_period=True,
    )

    data["frontend_requests"] = await get_requests_state(
        project_id=frontend_id,
        environment=frontend_env,
    )
    data["frontend_requests_prev"] = await get_requests_state(
        project_id=frontend_id,
        environment=frontend_env,
        preview_time_period=True,
    )

    data["backend"] = await get_backend_state(
        project_id=backend_id,
        environment=backend_env,
    )
    data["backend_prev"] = await get_backend_state(
        project_id=backend_id,
        environment=backend_env,
        preview_time_period=True,
    )

    data["backend_requests"] = await get_requests_state(
        project_id=backend_id,
        environment=backend_env,
    )
    data["backend_requests_prev"] = await get_requests_state(
        project_id=backend_id,
        environment=backend_env,
        preview_time_period=True,
    )

    data["cache"] = await get_cache_state(
        project_id=backend_id,
        environment=backend_env,
    )
    data["cache_prev"] = await get_cache_state(
        project_id=backend_id,
        environment=backend_env,
        preview_time_period=True,
    )

    data["queue"] = await get_queue_state(
        project_id=backend_id,
        environment=backend_env,
    )
    data["queue_prev"] = await get_queue_state(
        project_id=backend_id,
        environment=backend_env,
        preview_time_period=True,
    )

    data["database"] = await get_database_state(
        project_id=backend_id,
        environment=backend_env,
    )

    return data