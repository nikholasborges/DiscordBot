def valid_int(value):
    try:
        int(value)
        return True
    except ValueError:
        return False
