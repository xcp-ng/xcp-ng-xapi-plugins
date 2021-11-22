import json
import mock
import pytest
import XenAPIPlugin

from zfs import list_zfs_pools

@mock.patch('zfs.run_command', autospec=True)
class TestListZfsPools:
    def test_zfs(self, run_command):
        run_command.side_effect = [{"stdout": """vol0	type	filesystem	-
vol0	creation	Wed Jul 21 15:59 2021	-
vol0	used	161M	-
vol0	available	57.5G	-
vol0	referenced	160M	-
vol0	compressratio	1.00x	-
vol0	mounted	yes	-
vol0	quota	none	default
vol0	reservation	none	default
vol0	recordsize	128K	default
vol0	mountpoint	/vol0	default
vol0	sharenfs	off	default
vol0	checksum	on	default
vol0	compression	off	default
vol0	atime	on	default
vol0	devices	on	default
vol0	exec	on	default
vol0	setuid	on	default
vol0	readonly	off	default
vol0	zoned	off	default
vol0	snapdir	hidden	default
vol0	aclinherit	restricted	default
vol0	createtxg	1	-
vol0	canmount	on	default
vol0	xattr	on	default
vol0	copies	1	default
vol0	version	5	-
vol0	utf8only	off	-
vol0	normalization	none	-
vol0	casesensitivity	sensitive	-
vol0	vscan	off	default
vol0	nbmand	off	default
vol0	sharesmb	off	default
vol0	refquota	none	default
vol0	refreservation	none	default
vol0	guid	9952226885331160097	-
vol0	primarycache	all	default
vol0	secondarycache	all	default
vol0	usedbysnapshots	0B	-
vol0	usedbydataset	160M	-
vol0	usedbychildren	72K	-
vol0	usedbyrefreservation	0B	-
vol0	logbias	latency	default
vol0	objsetid	54	-
vol0	dedup	off	default
vol0	mlslabel	none	default
vol0	sync	standard	default
vol0	dnodesize	legacy	default
vol0	refcompressratio	1.00x	-
vol0	written	160M	-
vol0	logicalused	160M	-
vol0	logicalreferenced	160M	-
vol0	volmode	default	default
vol0	filesystem_limit	none	default
vol0	snapshot_limit	none	default
vol0	filesystem_count	none	default
vol0	snapshot_count	none	default
vol0	snapdev	hidden	default
vol0	acltype	off	default
vol0	context	none	default
vol0	fscontext	none	default
vol0	defcontext	none	default
vol0	rootcontext	none	default
vol0	relatime	off	default
vol0	redundant_metadata	all	default
vol0	overlay	off	default
vol0	encryption	off	default
vol0	keylocation	none	default
vol0	keyformat	none	default
vol0	pbkdf2iters	0	default
vol0	special_small_blocks	0	default"""}, OSError(2, 'Error!', 'Error!'), OSError(3, 'Error!', 'Error!')]

        expected = ' \
{"vol0": {"setuid": "on", "relatime": "off", "referenced": "160M", "written": "160M", "zoned": "off", \
"primarycache": "all", "logbias": "latency", "creation": "Wed Jul 21 15:59 2021", "sync": "standard", "snapdev": \
"hidden", "dedup": "off", "sharenfs": "off", "usedbyrefreservation": "0B", "sharesmb": "off", "createtxg": "1", \
"canmount": "on", "mountpoint": "/vol0", "casesensitivity": "sensitive", "utf8only": "off", "xattr": "on", \
"dnodesize": "legacy", "mlslabel": "none", "objsetid": "54", "defcontext": "none", "rootcontext": "none", "mounted": \
"yes", "compression": "off", "overlay": "off", "logicalused": "160M", "usedbysnapshots": "0B", "filesystem_count": \
"none", "copies": "1", "snapshot_limit": "none", "aclinherit": "restricted", "compressratio": "1.00x", "readonly": \
"off", "version": "5", "normalization": "none", "filesystem_limit": "none", "type": "filesystem", "secondarycache": \
"all", "refreservation": "none", "available": "57.5G", "used": "161M", "exec": "on", "refquota": "none", \
"refcompressratio": "1.00x", "quota": "none", "keylocation": "none", "snapshot_count": "none", "fscontext": "none", \
"vscan": "off", "reservation": "none", "atime": "on", "recordsize": "128K", "usedbychildren": "72K", "usedbydataset": \
"160M", "guid": "9952226885331160097", "pbkdf2iters": "0", "checksum": "on", "special_small_blocks": "0", \
"redundant_metadata": "all", "volmode": "default", "devices": "on", "keyformat": "none", "logicalreferenced": "160M", \
"acltype": "off", "nbmand": "off", "context": "none", "encryption": "off", "snapdir": "hidden"}}'
        res = list_zfs_pools(None, None)
        assert json.loads(res) == json.loads(expected)

        expected = '{}'
        res = list_zfs_pools(None, None)
        assert json.loads(res) == json.loads(expected)

        with pytest.raises(XenAPIPlugin.Failure) as e:
            list_zfs_pools(None, None)

        assert e.value.params[0] == '3'
        assert e.value.params[1] == 'Error!'

        assert run_command.call_count == 3
        run_command.assert_called_with(['zfs', 'get', '-H', 'all'])

    def test_zfs_error(self, run_command):
        run_command.side_effect = [Exception('Error!')]

        with pytest.raises(XenAPIPlugin.Failure) as e:
            list_zfs_pools(None, None)
        run_command.assert_called_once_with(['zfs', 'get', '-H', 'all'])
        assert e.value.params[0] == '-1'
        assert e.value.params[1] == 'Error!'
