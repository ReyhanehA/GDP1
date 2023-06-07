# -*- coding: utf-8 -*-
import pytest
import sys

from .test_base_class import TestBaseClass
from aerospike import exception as e

aerospike = pytest.importorskip("aerospike")
try:
    import aerospike
except:
    print("Please install aerospike python client.")
    sys.exit(1)


class TestScanInfo(object):

    def setup_method(self, method):
        """
        Setup method.
        """
        hostlist, user, password = TestBaseClass.get_hosts()
        config = {'hosts': hostlist}
        if user is None and password is None:
            self.client = aerospike.client(config).connect()
        else:
            self.client = aerospike.client(config).connect(user, password)
        for i in range(5):
            key = ('test', 'demo', i)
            rec = {'name': 'name%s' % (str(i)), 'age': i}
            self.client.put(key, rec)
        policy = {}
        self.client.udf_put("bin_lua.lua", 0, policy)
        self.job_id = self.client.scan_apply("test", "demo", "bin_lua",
                                             "mytransform", ['age', 2])

    def teardown_method(self, method):
        """
        Teardoen method.
        """
        for i in range(5):
            key = ('test', 'demo', i)
            self.client.remove(key)
        self.client.close()

    def test_job_info_with_no_parameters(self):
        """
        Invoke job_info() without any mandatory parameters.
        """
        with pytest.raises(TypeError) as typeError:
            self.client.job_info()
        assert "Required argument 'job_id' (pos 1) not found" in str(
            typeError.value)

    def test_job_info_with_correct_parameters(self):
        """
        Invoke job_info() with correct parameters
        """
        job_info = self.client.job_info(self.job_id, aerospike.JOB_SCAN)

        if job_info['status'] == aerospike.JOB_STATUS_COMPLETED or \
           job_info['status'] == aerospike.JOB_STATUS_UNDEF or \
           job_info['status'] or aerospike.JOB_STATUS_INPROGRESS:
            assert True is True
        else:
            assert True is False

    def test_job_info_with_correct_policy(self):
        """
        Invoke job_info() with correct policy
        """
        policy = {'timeout': 1000}
        job_info = self.client.job_info(
            self.job_id, aerospike.JOB_SCAN, policy)

        if job_info['status'] == aerospike.JOB_STATUS_COMPLETED or \
           job_info['status'] == aerospike.JOB_STATUS_UNDEF or \
           job_info['status'] or aerospike.JOB_STATUS_INPROGRESS:
            assert True is True
        else:
            assert True is False

    def test_job_info_with_incorrect_policy(self):
        """
        Invoke job_info() with incorrect policy
        """
        policy = {
            'timeout': 0.5
        }
        try:
            self.client.job_info(self.job_id, aerospike.JOB_SCAN, policy)

        except e.ParamError as exception:
            assert exception.code == -2
            assert exception.msg == "timeout is invalid"

    def test_job_info_with_scanid_negative(self):
        """
        Invoke job_info() with scan id negative
        """
        with pytest.raises(TypeError) as typeError:
            self.client.job_info(-2)
        assert "Required argument 'module' (pos 2) not found" in str(
            typeError.value)

    def test_job_info_with_scanid_incorrect(self):
        """
        Invoke job_info() with scan id incorrect
        """
        with pytest.raises(TypeError) as typeError:
            self.client.job_info(1)
        assert "Required argument 'module' (pos 2) not found" in str(
            typeError.value)

    def test_job_info_with_scanid_string(self):
        """
        Invoke job_info() with scan id incorrect
        """
        with pytest.raises(TypeError) as typeError:
            self.client.job_info("string")
        assert "an integer is required" in str(typeError.value)

    def test_job_info_with_correct_parameters_without_connection(self):
        """
        Invoke job_info() with correct parameters without connection
        """

        config = {'hosts': [('127.0.0.1', 3000)]}
        client1 = aerospike.client(config)

        try:
            client1.job_info(self.job_id, aerospike.JOB_SCAN)

        except e.ClusterError as exception:
            assert exception.code == 11
            assert exception.msg == 'No connection to aerospike cluster'
