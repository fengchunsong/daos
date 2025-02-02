#!/usr/bin/python
"""
  (C) Copyright 2018-2022 Intel Corporation.

  SPDX-License-Identifier: BSD-2-Clause-Patent
"""

from performance_test_base import PerformanceTestBase
from data_mover_test_base import DataMoverTestBase
from exception_utils import CommandFailure

import oclass_utils

class BasicCheckout(PerformanceTestBase):
    # pylint: disable=too-few-public-methods
    # pylint: disable=too-many-ancestors
    """Test Class Description: Test class wrapping up tests from four
                               different test classes into one. Intent
                               is to run these tests as a basic checkout
                               for newly installed servers.
    :avocado: recursive
    """

    def test_basiccheckout_sanity(self):
        """
        Test Description: Bundles four tests into one and run in the
                          following sequence - ior_small, mdtest_small,
                          ec_smoke and autotest.
        :avocado: tags=all,deployment,full_regression
        :avocado: tags=hw,large
        :avocado: tags=dfuse,ior,mdtest
        :avocado: tags=basiccheckout,basiccheckout_sanity
        """

        # ior easy
        self.run_performance_ior(namespace="/run/ior_dfs_sx/*", use_stonewalling_read=True)
        if self.num_servers >= oclass_utils.calculate_min_servers('EC_16P2GX'):
            self.run_performance_ior(namespace="/run/ior_dfs_ec_16p2gx/*",
                                     use_stonewalling_read=True)
        elif self.num_servers >= oclass_utils.calculate_min_servers('EC_8P2GX'):
            self.run_performance_ior(namespace="/run/ior_dfs_ec_8p2gx/*",
                                     use_stonewalling_read=True)

        # mdtest easy
        self.run_performance_mdtest(namespace="/run/mdtest_dfs_s1/*")
        if self.num_servers >= oclass_utils.calculate_min_servers('EC_16P2G1'):
            self.run_performance_mdtest(namespace="/run/mdtest_dfs_ec_16p2g1/*")
        elif self.num_servers >= oclass_utils.calculate_min_servers('EC_8P2G1'):
            self.run_performance_mdtest(namespace="/run/mdtest_dfs_ec_8p2g1/*")

        #run autotest
        self.log.info("Autotest start")
        daos_cmd = self.get_daos_command()
        try:
            daos_cmd.pool_autotest(pool=self.pool.uuid)
            self.log.info("daos pool autotest passed.")
        except CommandFailure as error:
            self.log.error("Error: %s", error)
            self.fail("daos pool autotest failed!")

    def test_basiccheckout_ior_mdtest_small(self):
        """
        Test Description: Run ior and mdtest small on random racks

        :avocado: tags=all,deployment,full_regression
        :avocado: tags=hw,large
        :avocado: tags=ior,mdtest
        :avocado: tags=basiccheckout,basiccheckout_ior_mdtest_small
        """

        # local param
        flags = self.params.get("ior_flags", '/run/ior/iorflags/*')
        apis = self.params.get("ior_api", '/run/ior/iorflags/*')
        dfuse_mount_dir = self.params.get("mount_dir", "/run/dfuse/*")
        transfer_block_size = self.params.get("transfer_block_size",
                                              '/run/ior/iorflags/*')
        obj_class = self.params.get("obj_class", '/run/ior/iorflags/*')
        ec_obj_class = self.params.get("ec_oclass", '/run/ior/*')
        mdtest_params = self.params.get("mdtest_params", "/run/mdtest/*")

        #run ior
        results = self.run_ior_multiple_variants(obj_class, apis, transfer_block_size,
                                                 flags, dfuse_mount_dir)

        #run ior with different ec oclass
        results_ec = self.run_ior_multiple_variants(ec_obj_class, [apis[0]],
                                                    [transfer_block_size[1]],
                                                    [flags[0]], dfuse_mount_dir)
        results = results + results_ec
        self.log.info("Summary of IOR small test results:")
        errors = False
        for item in results:
            self.log.info("  %s  %s", item[0], item[1])
            if item[0] == "FAIL":
                errors = True
        if errors:
            self.fail("Test FAILED")

        #run mdtest
        self.run_mdtest_multiple_variants(mdtest_params)


class BasicCheckoutDm(DataMoverTestBase):
    # pylint: disable=too-few-public-methods
    # pylint: disable=attribute-defined-outside-init
    # pylint: disable=too-many-ancestors
    """Test Class Description: Test class to wrap datamover test to
                               run as part of basic checkout and verify
                               connectivity for lustre FS
    :avocado: recursive
    """

    def test_basic_checkout_dm(self):
        """
        Test Description: Datamover test to check connection and datamover
                          functionality with Lustre fs on newly installed
                          server nodes.
        :avocado: tags=all,deployment,full_regression
        :avocado: tags=hw,large
        :avocado: tags=datamover,fs_copy,ior
        :avocado: tags=basiccheckout,basiccheckout_dm
        """
        # load ior params for dm test
        self.ior_cmd.namespace = "/run/ior_dm/*"
        self.ior_cmd.get_params(self)
        self.ppn = self.params.get("ppn", '/run/ior_dm/client_processes/*')
        #run datamover
        self.run_dm_activities_with_ior("FS_COPY", True)
