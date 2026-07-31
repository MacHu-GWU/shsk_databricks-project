
.. image:: https://readthedocs.org/projects/shsk-databricks/badge/?version=latest
    :target: https://shsk-databricks.readthedocs.io/en/latest/
    :alt: Documentation Status

.. image:: https://github.com/MacHu-GWU/shsk_databricks-project/actions/workflows/main.yml/badge.svg
    :target: https://github.com/MacHu-GWU/shsk_databricks-project/actions?query=workflow:CI

.. image:: https://codecov.io/gh/MacHu-GWU/shsk_databricks-project/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/MacHu-GWU/shsk_databricks-project

.. image:: https://img.shields.io/pypi/v/shsk-databricks.svg
    :target: https://pypi.python.org/pypi/shsk-databricks

.. image:: https://img.shields.io/pypi/l/shsk-databricks.svg
    :target: https://pypi.python.org/pypi/shsk-databricks

.. image:: https://img.shields.io/pypi/pyversions/shsk-databricks.svg
    :target: https://pypi.python.org/pypi/shsk-databricks

.. image:: https://img.shields.io/badge/✍️_Release_History!--None.svg?style=social&logo=github
    :target: https://github.com/MacHu-GWU/shsk_databricks-project/blob/main/release-history.rst

.. image:: https://img.shields.io/badge/⭐_Star_me_on_GitHub!--None.svg?style=social&logo=github
    :target: https://github.com/MacHu-GWU/shsk_databricks-project

------

.. image:: https://img.shields.io/badge/Link-API-blue.svg
    :target: https://shsk-databricks.readthedocs.io/en/latest/py-modindex.html

.. image:: https://img.shields.io/badge/Link-Install-blue.svg
    :target: `install`_

.. image:: https://img.shields.io/badge/Link-GitHub-blue.svg
    :target: https://github.com/MacHu-GWU/shsk_databricks-project

.. image:: https://img.shields.io/badge/Link-Submit_Issue-blue.svg
    :target: https://github.com/MacHu-GWU/shsk_databricks-project/issues

.. image:: https://img.shields.io/badge/Link-Request_Feature-blue.svg
    :target: https://github.com/MacHu-GWU/shsk_databricks-project/issues

.. image:: https://img.shields.io/badge/Link-Download-blue.svg
    :target: https://pypi.org/pypi/shsk-databricks#files


Welcome to ``shsk_databricks`` Documentation
==============================================================================
.. image:: https://shsk-databricks.readthedocs.io/en/latest/_static/shsk_databricks-logo.png
    :target: https://shsk-databricks.readthedocs.io/en/latest/

``shsk_databricks`` is a collection of `Claude Code <https://claude.com/claude-code>`_ agent
skills for working with `Databricks <https://www.databricks.com/>`_. The skills are packaged as
a Claude Code plugin named ``databricks``, laid out under ``.claude/skills/databricks/``, so each
one is loaded on demand when the conversation actually calls for it rather than sitting in the
agent's context all the time.

As of 0.1.1 the plugin ships a single skill, ``databricks-docs``. It answers Databricks questions
from the official documentation at the moment you ask, instead of from whatever the model happened
to learn before its training cutoff — which matters for a vendor that renames things as often as
Databricks does (``dlt/`` became ``ldp/``, Delta Live Tables became Lakeflow Declarative
Pipelines, Workflows became Lakeflow Jobs). It searches a locally cached copy of the
``docs.databricks.com`` ``llms.txt`` index — 252 entries across 15 sections — feeds only the
matching lines into context, and then reads just the pages that matched. More Databricks skills
will be added to the same plugin over time.


.. _install:

Install
------------------------------------------------------------------------------

``shsk_databricks`` is released on PyPI, so all you need is to:

.. code-block:: console

    $ pip install shsk-databricks

To upgrade to latest version:

.. code-block:: console

    $ pip install --upgrade shsk-databricks
