
def format_rtc_now_as_stings(n):
    y = str(n[0])

    M = str(n[1])
    if n[1] < 10:
        M = '0'+str(n[1])

    d = str(n[2])
    if n[2] < 10:
        d = '0'+str(n[2])

    h = str(n[3])
    if n[3] < 10:
        h = '0'+str(n[3])

    m = str(n[4])
    if n[4] < 10:
        m = '0'+str(n[4])

    S = str(n[5])
    if n[5] < 10:
        S = '0'+str(n[5])

    s = str(n[6])
    if n[6] < 10:
        s = '00000'+str(n[6])
    elif n[6] < 100:
        s = '0000'+str(n[6])
    elif n[6] < 1000:
        s = '000'+str(n[6])
    elif n[6] < 10000:
        s = '00'+str(n[6])
    elif n[6] < 100000:
        s = '0'+str(n[6])

    return (y, M, d, h, m, S, s)


def format_rtc_now_as_iso_string(n):
    """Format the tuple returned by rtc.now() as an ISO 8601 UTC date and time format.
        eg. '2020-06-05T21:44:20.025Z'
    """
    y = str(n[0])

    M = str(n[1])
    if n[1] < 10:
        M = '0'+str(n[1])

    d = str(n[2])
    if n[2] < 10:
        d = '0'+str(n[2])

    h = str(n[3])
    if n[3] < 10:
        h = '0'+str(n[3])

    m = str(n[4])
    if n[4] < 10:
        m = '0'+str(n[4])

    s = str(n[5])
    if n[5] < 10:
        S = '0'+str(n[5])

    ms = str(int(round(n[6]/1000)))
    if n[6] < 10:
        ms = '00000'+str(n[6])
    elif n[6] < 100:
        ms = '0000'+str(n[6])
    elif n[6] < 1000:
        ms = '000'+str(n[6])
    elif n[6] < 10000:
        ms = '00'+str(n[6])
    elif n[6] < 100000:
        ms = '0'+str(n[6])

    iso = '{}-{}-{}T{}:{}:{}.{}Z'.format(y, M, d, h, m, s, ms)

    return iso
