def fmt_percentage(value):
    return f"{value:.1%}"


def fmt_percentage_signed(value):
    return f"{value:+.1%}"


def fmt_duration(value):
    # TODO: make into s,m,h,d,wk,mo,yr
    return f"{value:.2f}ms"
