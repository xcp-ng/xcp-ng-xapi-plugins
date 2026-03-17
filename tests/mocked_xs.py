class Xs:
    def __init__(self, data):
        """
        Create a mock Xs object.

        Parameters
        ----------
        data: dict
            Nested dictionary of Xenstore elements, with "" being the key of an
            element if that element has a child.

        """
        self._data = data
        self._tx = 0
        self._txs = set()

    def close(self):
        self._data = None
        self._tx = 0
        self._txs = set()

    def get_domain_path(self, domid):
        assert isinstance(domid, int)
        return "/local/domain/{0}".format(domid)

    def transaction_start(self):
        tx = str(self._tx)
        self._txs.add(tx)
        self._tx += 1
        return tx

    def transaction_end(self, tx):
        self._txs.remove(tx)

    @staticmethod
    def _explode(path):
        assert path
        if not path.startswith("/"):
            path = "/local/domain/0" + path
        return path.strip("/").split("/")

    def _traverse(self, segs):
        current = self._data
        while segs:
            if current is None or isinstance(current, str):
                current = None
                break
            current = current.get(segs[0])
            segs = segs[1:]
        return current

    def ls(self, tx, path):
        assert self._data is not None
        assert tx in self._txs
        segs = self._explode(path)
        current = self._traverse(segs)
        if current is None:
            return None
        return list(filter(lambda key: bool(key), current.keys()))

    def read(self, tx, path):
        assert self._data is not None
        assert tx in self._txs
        segs = self._explode(path)
        current = self._traverse(segs)
        if isinstance(current, str):
            return current.encode()
        elif current is None:
            return current
        else:
            data = current.get("")
            if data is None:
                return None
            else:
                return data.encode()
