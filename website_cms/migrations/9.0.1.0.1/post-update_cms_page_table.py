#-*- coding: utf-8 -*-

import logging
from openerp.modules.registry import RegistryManager


def get_logger():
    name = '[website_cms.migration]'
    return logging.getLogger(name)


def migrate(cr, version):
    logger = get_logger()
    registry = RegistryManager.get(cr.dbname)
    ids = registry['cms.page'].search(cr, 1, [])
    pages = registry['cms.page'].browse(cr, 1, ids)
    for item in pages:
        item.write({'path': item.build_path(item)})
    logger.info('Upgrade cms.page paths')
