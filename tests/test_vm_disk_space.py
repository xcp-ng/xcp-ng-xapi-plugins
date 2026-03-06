import pytest
import mocked_xs

from vm_disk_space import vm_list_volumes, volume_get

DATA = {
    "local": {
        "domain": {
            "1": {
                "data": {
                    "volumes": {
                        "0": {
                            "driveletter": "C:",
                            "extents": {
                                "0": {
                                    "": "xvda",
                                    "diskid": "0",
                                    "length": "33685504000",
                                    "offset": "122683392",
                                    "target": "0",
                                }
                            },
                            "filesystem": "NTFS",
                            "free": "16663138304",
                            "mount_points": {
                                "0": "C:\\",
                            },
                            "name": "\\\\?\\Volume{5989a8d9-8809-410e-b9ea-1246b17ce272}\\",
                            "size": "33685499904",
                            "volume_name": "",
                        },
                        "1": {
                            "driveletter": "",
                            "extents": {
                                "0": {
                                    "": "xvda",
                                    "diskid": "0",
                                    "length": "549453824",
                                    "offset": "33808187392",
                                    "target": "0",
                                }
                            },
                            "filesystem": "NTFS",
                            "free": "89468928",
                            "name": "\\\\?\\Volume{4cbc9991-9ed1-4527-a3a4-29d1b6d451c2}\\",
                            "size": "549449728",
                            "volume_name": "",
                        },
                        "2": {
                            "driveletter": "",
                            "extents": {
                                "0": {
                                    "": "xvda",
                                    "diskid": "0",
                                    "length": "104857600",
                                    "offset": "1048576",
                                    "target": "0",
                                }
                            },
                            "filesystem": "FAT32",
                            "free": "71124992",
                            "name": "\\\\?\\Volume{8d79687c-caff-4b4f-beb4-31038b6468c2}\\",
                            "size": "100663296",
                            "volume_name": "",
                        },
                        "3": {
                            "driveletter": "D:",
                            "extents": {
                                "0": {
                                    "": "xvdd",
                                    "target": "3",
                                }
                            },
                            "filesystem": "",
                            "free": "0",
                            "mount_points": {
                                "0": "D:\\",
                            },
                            "name": "\\\\?\\Volume{12050cbd-7c8f-11ef-8f8d-806e6f6e6963}\\",
                            "size": "0",
                            "volume_name": "",
                        },
                    }
                }
            },
            "2": {
                "data": {
                    "volumes": {
                        "0": {
                            "extents": {
                                "0": "xvda",
                            },
                            "free": "2005835776",
                            "name": "/dev/xvda1",
                            "size": "1048576",
                        },
                        "1": {
                            "extents": {
                                "0": "xvda",
                            },
                            "filesystem": "ext4",
                            "free": "17410916352",
                            "mount_points": {
                                "0": "/",
                            },
                            "name": "/dev/xvda2(8f6d7cd7-4435-4f3a-9811-ba9c957a45b4)",
                            "size": "26841431552",
                        },
                    }
                }
            },
            "3": {},
        }
    }
}


@pytest.fixture(scope="class")
def xs():
    return mocked_xs.Xs(DATA)


@pytest.fixture(scope="function")
def tx(xs):
    tx = xs.transaction_start()
    yield tx
    xs.transaction_end(tx)


class TestVmDiskSpace:
    def test_volumes_count(self, xs, tx):
        assert len(list(vm_list_volumes(xs, tx, "/local/domain/1/data/volumes"))) == 4
        assert len(list(vm_list_volumes(xs, tx, "/local/domain/2/data/volumes"))) == 2
        assert len(list(vm_list_volumes(xs, tx, "/local/domain/3/data/volumes"))) == 0

    def test_volume_windows(self, xs, tx):
        volume = volume_get(xs, tx, "/local/domain/1/data/volumes/0")
        assert volume["driveletter"] == "C:"
        assert len(volume["extents"]) == 1
        assert volume["extents"][0][""] == "xvda"
        assert volume["extents"][0]["diskid"] == 0
        assert volume["extents"][0]["length"] == 33685504000
        assert volume["size"] == 33685499904
        assert volume["free"] == 16663138304

    def test_volume_windows_2(self, xs, tx):
        volume = volume_get(xs, tx, "/local/domain/1/data/volumes/1")
        assert volume["driveletter"] == ""
        assert "mount_points" not in volume

    def test_volume_linux(self, xs, tx):
        volume = volume_get(xs, tx, "/local/domain/2/data/volumes/0")
        assert len(volume["extents"]) == 1
        assert "driveletter" not in volume
        assert volume["extents"][0][""] == "xvda"
        assert "diskid" not in volume["extents"][0]
        assert volume["size"] == 1048576
        assert volume["free"] == 2005835776
