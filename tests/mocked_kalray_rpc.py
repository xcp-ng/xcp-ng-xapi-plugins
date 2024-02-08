class HTTPJSONRPCClient(object):
    def __init__(self, addr, port=None, timeout=60.0, user='admin', password='admin', **kwargs):
        pass

    def call(self, method, params=None):
        """We will juste check that parameters are ok."""
        parameters = {
            "bdev_get_bdevs": {
                "required": [],
                "optional": ['name', 'timeout'],
            },
            "bdev_raid_get_bdevs": {
                "required": ['category'],
                "optional": [],
            },
            "bdev_lvol_get_lvstores": {
                "required": [],
                "optional": ['uuid', 'lvs_name'],
            },
            "bdev_raid_create": {
                "required": ['name', 'strip_size_kb', 'raid_level', 'base_bdevs'],
                "optional": ['persist', 'split_dp'],
            },
            "bdev_lvol_create_lvstore": {
                "required": ['bdev_name', 'lvs_name'],
                "optional": ['cluster_sz', 'clear_method', 'num_md_pages_per_cluster_ratio'],
            },
            "bdev_lvol_create": {
                "required": ['lvol_name'],
                "optional": ['size', 'size_in_mib', 'thin_provision', 'uuid', 'lvs_name', 'clear_method'],
            },
            "bdev_lvol_delete": {
                "required": ['name'],
                "optional": [],
            },
        }

        # Check that method is mocked
        try:
            p = parameters[method]
        except KeyError:
            assert False, f"{method} is not mocked"

        # Check that required parameters are given
        for k in p['required']:
            assert k in params, f"Required parameter '{k}' is missing for {method}"

        # Check that params passed to method are valid
        for k in params:
            assert k in p['required'] or k in p['optional'], f"Invalid parameter '{k}' for {method}"


class JSONRPCException(BaseException):
    def __init__(self, message):
        assert False, "Mock me!"
