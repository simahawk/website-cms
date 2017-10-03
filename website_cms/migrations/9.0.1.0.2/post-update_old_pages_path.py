# -*- coding: utf-8 -*-

# flake8: noqa

import logging
from openerp.modules.registry import RegistryManager


def get_logger():
    """Return a logger."""
    name = '[website_cms.migration]'
    return logging.getLogger(name)


def migrate(cr, version):
    logger = get_logger()
    # a bug in frontend page form was overriding path on edit
    # let's fix db data
    logger.info('Upgrade cms.page paths: START')
    registry = RegistryManager.get(cr.dbname)
    ids = registry['cms.page'].search(cr, 1, [])
    pages = registry['cms.page'].browse(cr, 1, ids)
    for item in pages:
        item._compute_path()
    logger.info('Upgrade cms.page paths: STOP')
