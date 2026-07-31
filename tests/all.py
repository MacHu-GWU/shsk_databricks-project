# -*- coding: utf-8 -*-

if __name__ == "__main__":
    from shsk_databricks.tests import run_cov_test

    run_cov_test(
        __file__,
        "shsk_databricks",
        is_folder=True,
        preview=False,
    )
