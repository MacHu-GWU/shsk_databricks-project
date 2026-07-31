# -*- coding: utf-8 -*-

from shsk_databricks import api


def test():
    _ = api


if __name__ == "__main__":
    from shsk_databricks.tests import run_cov_test

    run_cov_test(
        __file__,
        "shsk_databricks.api",
        preview=False,
    )
