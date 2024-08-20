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