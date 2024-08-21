# Those are the thresholds that define if it is a good, meh, or poor value for each metric.
THRESHOLDS = {
    "ttfb": [200, 400],
    "fcp": [1000, 3000],
    "inp": [200, 400],
    "http_failure_rate": [0.02, 0.05],
    "http_avg_duration": [800, 1500],
    "backend_failure_rate": [0.02, 0.05],
    "inverse_apdex": [0.1, 0.3],
    "cache_miss_rate": [0.1, 0.3],
    "queue_avg_processing": [200, 800],
    "queue_avg_time_in_queue": [200, 800],
}


def get_score(metric, value):
    thresholds = THRESHOLDS.get(metric)
    if not thresholds:
        return None

    if value < thresholds[0]:
        return "Good"

    if value >= thresholds[0] and value < thresholds[1]:
        return "Meh"

    return "Poor"


def fmt_percentage(value):
    return f"{value:.1%}"


def fmt_percentage_signed(value):
    return f"{value:+.1%}"


def fmt_duration(value):
    if value < 1000:
        return f"{value:.1f}ms"

    value /= 1000
    if value < 60:
        return f"{value:.1f}s"

    value /= 60
    if value < 60:
        return f"{value:.1f}m"

    value /= 60
    if value < 24:
        return f"{value:.1f}h"

    value /= 24
    if value < 7:
        return f"{value:.1f}d"

    value /= 7
    if value < 4:
        return f"{value:.1f}wk"

    value /= 4
    if value < 12:
        return f"{value:.1f}mo"

    value /= 12
    return f"{value:.1f}yr"


def fmt_round_2(value):
    return f"{value:.2f}"
