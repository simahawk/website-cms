# Copyright 2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields


class FakeModelMixin(object):

    @classmethod
    def _test_setup(cls, env):
        """Initialize test model.

        Inspired by SBidoul in https://github.com/OCA/mis-builder :)
        """
        cls._build_model(env.registry, env.cr)
        env.registry.setup_models(env.cr)
        env.registry.init_models(
            env.cr, [cls._name],
            dict(env.context, update_custom_fields=True)
        )

    @classmethod
    def _test_teardown(cls, env):
        """Teaardown test model.

        Inspired by SBidoul in https://github.com/OCA/mis-builder :)
        """
        if not getattr(cls, '_teardown_no_delete', False):
            del env.registry.models[cls._name]
        env.registry.setup_models(env.cr)


class OrderableModel(models.Model, FakeModelMixin):
    """A test model that implements `cms.orderable.mixin`."""

    _name = 'fake.orderable'
    _description = 'cms_mixin: orderable test model'
    _inherit = [
        'cms.orderable.mixin',
    ]
    name = fields.Char()


class CoremetadataModel(models.Model, FakeModelMixin):
    """A test model that implements `cms.coremetadata.mixin`."""

    _name = 'fake.coremetadata'
    _description = 'cms_mixin: coremetadata test model'
    _inherit = [
        'website.published.mixin',
        'cms.coremetadata.mixin',
    ]
    name = fields.Char()


class ContentModel(models.Model, FakeModelMixin):
    """A test model that implements `cms.content.mixin`."""

    _name = 'fake.content'
    _description = 'cms_mixin: content test model'
    _inherit = [
        'cms.content.mixin',
    ]
