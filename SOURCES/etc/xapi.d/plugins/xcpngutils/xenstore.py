import contextlib


@contextlib.contextmanager
def xs_open():
    import xen.lowlevel.xs

    xs = xen.lowlevel.xs.xs()
    try:
        yield xs
    finally:
        xs.close()


@contextlib.contextmanager
def xs_transaction(xs):
    tx = xs.transaction_start()
    try:
        yield tx
    finally:
        xs.transaction_end(tx)


def xs_join(a, b):
    if a is None:
        a = ""
    if b and b.startswith("/"):
        raise Exception("attempting to join an absolute path")
    if not b:
        return a.rstrip("/")
    elif a.endswith("/"):
        return a + b
    else:
        return a + "/" + b


def xs_read(xs, tx, path):
    data = xs.read(tx, path)
    if data is None:
        return None
    else:
        return data.decode()
