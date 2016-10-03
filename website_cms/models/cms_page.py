# -*- coding: utf-8 -*-

# pylint: disable=E0401
# pylint: disable=W0212
import math
from openerp.http import request
from openerp import models
from openerp import fields
from openerp import api
from openerp import exceptions
from openerp import tools
from openerp.tools.translate import _
from openerp.tools.translate import html_translate
from openerp.addons.base.ir.ir_ui_view import keep_query
from openerp.addons.website.models.website import slug
from openerp.addons.website.models.website import unslug
from openerp.addons.website_cms.utils import AttrDict


def to_slug(item):
    """Force usage of item.name."""
    value = (item.id, item.name)
    return slug(value)


VIEW_DOMAIN = [
    ('type', '=', 'qweb'),
    ('cms_view', '=', True),
]
SIDEBAR_VIEW_DOMAIN = [
    ('type', '=', 'qweb'),
    ('cms_sidebar', '=', True),
]


class CMSPage(models.Model):
    """Model of a CMS page."""

    _name = 'cms.page'
    _description = 'CMS page'
    _order = 'sequence, id'
    _inherit = ['website.seo.metadata',
                'website.published.mixin',
                'website.image.mixin',
                'website.orderable.mixin',
                'website.coremetadata.mixin',
                'website.security.mixin',
                'website.redirect.mixin']

    name = fields.Char(
        'Name',
        required=True,
        translate=True,
    )
    description = fields.Text(
        'Description',
        translate=True,
    )
    body = fields.Html(
        'HTML Body',
        translate=html_translate,
        sanitize=False
    )
    parent_id = fields.Many2one(
        string='Parent',
        comodel_name='cms.page',
        domain=lambda self: self._domain_parent_id(),
    )
    children_ids = fields.One2many(
        string='Children',
        inverse_name='parent_id',
        comodel_name='cms.page'
    )
    related_ids = fields.Many2many(
        string='Related pages',
        comodel_name='cms.page',
        relation='cms_page_related_rel',
        column1='from_id',
        column2='to_id',
    )
    tag_ids = fields.Many2many(
        string='Tags',
        comodel_name='cms.tag',
        relation='cms_page_related_tag_rel',
        column1='page_id',
        column2='tag_id',
    )
    # XXX 2016-03-30: we are not using this anymore
    # because we can use cms.media since a while.
    # It might be useful for other purposes,
    # let's keep it for a while.
    attachment_ids = fields.One2many(
        string='Attachments',
        inverse_name='res_id',
        comodel_name='ir.attachment'
    )
    media_ids = fields.One2many(
        string='Media items',
        inverse_name='res_id',
        comodel_name='cms.media'
    )
    type_id = fields.Many2one(
        string='Page type',
        comodel_name='cms.page.type',
        default=lambda self: self._default_type_id()
    )
    view_id = fields.Many2one(
        string='View',
        comodel_name='ir.ui.view',
        domain=lambda self: VIEW_DOMAIN,
        default=lambda self: self._default_view_id()
    )
    sub_page_type_id = fields.Many2one(
        string='Default page type for sub pages',
        comodel_name='cms.page.type',
        help=(u"You can select a page type to be used "
              u"by default for each contained page."),
    )
    sub_page_view_id = fields.Many2one(
        string='Default page view for sub pages',
        comodel_name='ir.ui.view',
        help=(u"You can select a view to be used "
              u"by default for each contained page."),
        domain=lambda self: VIEW_DOMAIN,
    )
    list_types_ids = fields.Many2many(
        string='Types to list',
        comodel_name='cms.page.type',
        help=(u"You can select types of page to be used "
              u"in `listing` views."),
    )
    sidebar_view_ids = fields.Many2many(
        string='Sidebar views',
        comodel_name='ir.ui.view',
        help=(u"Each view linked here will be rendered in the sidebar."),
        domain=lambda self: SIDEBAR_VIEW_DOMAIN,
    )
    sidebar_content = fields.Html(
        'Sidebar HTML',
        translate=html_translate,
        sanitize=False,
        help=(u"Each template that enables customization in the sidebar "
              u"must use this field to store content."),
    )
    # sidebar_inherit = fields.Boolean(
    #     'Sidebar Inherit',
    #     help=(u"If turned on, you'll see the same sidebar "
    #           u"into each contained page."),
    # )
    nav_include = fields.Boolean(
        'Nav include',
        default=False,
        help=(u"Decide if this item "
              u"should be included in main navigation."),
    )
    path = fields.Char(
        string='Path',
        compute='_compute_path',
        readonly=True,
        store=True,
        copy=False,
        oldname='hierarchy'
    )
    default_view_item_id = fields.Many2one(
        string='Default view item',
        comodel_name='cms.page',
        help=(u"Selet an item to be used as default view "
              u"for current page. "),
    )

    @api.multi
    def write(self, vals):
        """Make sure to refresh website nav cache."""
        self.ensure_one()
        if 'nav_include' in vals:
            self.env['website'].clear_caches()
        return super(CMSPage, self).write(vals)

    @api.model
    def create(self, vals):
        """Make sure to refresh website nav cache."""
        res = super(CMSPage, self).create(vals)
        if 'nav_include' in vals:
            self.env['website'].clear_caches()
        return res

    @api.multi
    def unlink(self):
        """Override to prevent deletion of pages w/ media attached."""
        # look for attached media
        # and prevent deletion
        media = self.env['cms.media'].search([('res_id', 'in', self.ids)])
        if media:
            msg = _(u"You are trying to delete a page "
                    u"that has media items attached to it!")
            raise exceptions.Warning(msg)
        return super(CMSPage, self).unlink()

    @api.model
    def _domain_parent_id(self):
        # make sure we don't put sub-pages into news
        # or any other unforeseen type
        page_type = self.env.ref('website_cms.default_page_type')
        return [('type_id', '=', page_type.id)]

    @api.multi
    @api.constrains('parent_id')
    def _check_parent_id(self):
        """Make sure we cannot have parent = self."""
        self.ensure_one()
        if self.parent_id and self.parent_id.id == self.id:
            raise exceptions.ValidationError(
                _(u'You cannot set the parent of a page '
                  u'equal to the page itself. Page: "%s"') % self.name
            )

    @api.model
    def _default_type_id(self):
        page_type = self.env.ref('website_cms.default_page_type')
        return page_type and page_type.id or False

    @api.model
    def _default_view_id(self):
        page_view = self.env.ref('website_cms.page_default')
        return page_view and page_view.id or False

    @api.model
    def build_public_url(self, item):
        """Walk trough page path to build its public URL."""
        # XXX: this could be expensive... think about it!
        # We could store it but then we need to update
        # all the pages below a certain parent
        # if the parent name changes or if a parent is moved/changed.
        # We have the same problem with path: check for comment there.
        # In the end the url will work nonetheless because
        # the slug contains the object id
        # but the path in the url will be wrong.
        # Also, not using parents name to build the path
        # is bad because we miss the categorization
        # provided by each parents, that's good for
        # good URLs, and you allow ppl to not
        # put in each page name/title a whole keyworded
        # description of the content itself.
        current = item
        parts = [to_slug(current), ]
        while current.parent_id:
            parts.insert(0, to_slug(current.parent_id))
            current = current.parent_id
        public_url = '/cms/' + '/'.join(parts)
        return public_url

    @api.multi
    def _website_url(self, field_name, arg):
        """Override method defined by `website.published.mixin`."""
        res = {}
        for item in self:
            res[item.id] = self.build_public_url(item)
        return res

    # XXX: how to update path for the whole hierarchy
    # whenever and ancestor parent/name
    # - no matter the level -  is updated?
    # Right now we are supporting explicitely 3 levels,
    # but is not nice and it limits your hierarchy
    # We could override the write
    # and trigger updating of path for all the items
    # in the same path: but how to get this???
    @api.multi
    @api.depends('parent_id',
                 'parent_id.parent_id',
                 'parent_id.parent_id.parent_id',
                 'parent_id.parent_id.parent_id.parent_id')
    def _compute_path(self):
        for item in self:
            item.path = self.build_path(item)

    @property
    @api.model
    def hierarchy(self):
        """Walk trough page hierarchy and get a list of items."""
        self.ensure_one()
        if not self.parent_id:
            return ()
        current = self
        parts = []
        while current.parent_id:
            parts.insert(0, current.parent_id)
            current = current.parent_id
        return parts

    @api.model
    def build_path(self, item):
        """Walk trough page hierarchy to build its nested name."""
        if not item.parent_id:
            return '/'
        parts = [x.name for x in item.hierarchy]
        parts.insert(0, '')
        return '/'.join(parts)

    @api.model
    def full_path(self, item=None):
        """Full path for this item: includes item part."""
        item = item or self
        if not item.parent_id:
            return item.path + item.name
        return item.path + '/' + item.name

    @api.multi
    def name_get(self):
        """Format displayed name."""
        if not self.env.context.get('include_path'):
            return super(CMSPage, self).name_get()
        res = []
        for item in self:
            res.append((item.id,
                        item.path.rstrip('/') + '/' + item.name))
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        """Allow search in path too."""
        args = args or []
        domain = []
        if name and self.env.context.get('include_path'):
            domain = [
                '|',
                ('name', operator, name),
                ('path', operator, name),
            ]
        items = self.search(domain + args, limit=limit)
        return items.name_get()

    @api.model
    def get_root(self, item=None, upper_level=0):
        """Walk trough page path to find root ancestor.

        URL is made of items' slug so we can jump
        at any level by looking at path parts.

        Use `upper_level` to stop walking at a precise
        hierarchy level.
        """
        item = item or self
        # 1st bit is `/cms`
        bits = item.website_url.split('/')[2:]
        try:
            _slug = bits[upper_level]
        except IndexError:
            # safely default to real root
            _slug = bits[0]
        _, page_id = unslug(_slug)
        return self.browse(page_id)

    @api.multi
    def update_published(self):
        """Publish / Unpublish this page right away."""
        self.write({'website_published': not self.website_published})

    @api.multi
    def open_children(self):
        """Action to open tree view of children pages."""
        self.ensure_one()
        domain = [
            ('parent_id', '=', self.id),
        ]
        context = {
            'default_parent_id': self.id,
        }
        for k in ('type_id', 'view_id'):
            fname = 'sub_page_' + k
            value = getattr(self, fname)
            if value:
                context['default_' + k] = value.id
        return {
            'name': 'Children',
            'type': 'ir.actions.act_window',
            'res_model': 'cms.page',
            'target': 'current',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': domain,
            'context': context,
        }

    @api.multi
    def open_media(self):
        """Action to open tree view of contained media."""
        self.ensure_one()
        domain = [
            ('page_id', '=', self.id),
        ]
        context = {
            'default_page_id': self.id,
        }
        return {
            'name': 'Media',
            'type': 'ir.actions.act_window',
            'res_model': 'cms.media',
            'target': 'current',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': domain,
            'context': context,
        }

    @api.model
    def get_listing(self, published=True,
                    nav=None, types_ids=None,
                    order=None, item=None,
                    path=None, types_ref=None,
                    incl_tags=False, tag_ids=None):
        """Return items to be listed.

        Tweak filtering by:

        `published` to show published/unpublished items
            "website_cms.cms_manager" group bypass this;
        `nav` to show nav-included items;
        `types_ids` to limit listing to specific page types;
        `types_ref` to limit listing to specific page types;
            by xmlid refs
        `order` to override ordering by sequence;
        `path` to search in a specific path instead of
            just listing current item's children;
        `incl_tags` to include items related by same tags;
        `tag_ids` to filter upone specific tags.

        By default filter w/ `list_types_ids` if valued.
        """
        item = item or self
        base_domain = []
        # use specific `published` items but bypass it if manager
        if published is not None and \
                not self.env.user.has_group('website_cms.cms_manager'):
            base_domain.append(('website_published', '=', published))

        if nav is not None:
            base_domain.append(('nav_include', '=', nav))

        if types_ref:
            if isinstance(types_ref, basestring):
                types_ref = (types_ref, )
            types_ids = [self.env.ref(x).id for x in types_ref]

        types_ids = types_ids or (
            item.list_types_ids and item.list_types_ids.ids)

        if types_ids:
            base_domain.append(
                ('type_id', 'in', types_ids)
            )

        hierarchy_domain = []
        if path is None:
            hierarchy_domain.append(('parent_id', '=', item.id))
        else:
            hierarchy_domain.append(('path', '=like', path + '%'))

        # handle domain for tags
        tags_domain = []
        if incl_tags or tag_ids:
            # we want to apply the same criterias for all items
            # so we merge the base domain
            tag_ids = tag_ids or item.tag_ids.ids
            if tag_ids:
                tags_domain = [
                    ('tag_ids', 'in', tag_ids),
                ] + base_domain
                # plus we exclude the current item
                # if we are looking up by path
                if path is None:
                    tags_domain.append(('id', '!=', item.id, ))

        # prepare final domain
        # XXX: this could be done better...
        domain = []
        if tags_domain:
            if len(base_domain + hierarchy_domain) > 1:
                domain = ['|', '&', ] + \
                    base_domain + hierarchy_domain
            else:
                domain = ['|', ] + \
                    base_domain + hierarchy_domain
            if len(tags_domain) > 1:
                domain += ['&'] + tags_domain
            else:
                domain += tags_domain
        else:
            domain = base_domain + hierarchy_domain

        order = order or 'sequence asc'
        pages = self.search(domain, order=order)
        return pages

    def pager(self, total, page=1, step=10,
              scope=5, base_url='', url_getter=None):
        """Custom pager implementation."""
        # Compute Pager
        page_count = int(math.ceil(float(total) / step))

        page = max(1, min(int(page if str(page).isdigit() else 1), page_count))
        scope -= 1

        pmin = max(page - int(math.floor(scope / 2)), 1)
        pmax = min(pmin + scope, page_count)

        if pmax - pmin < scope:
            pmin = pmax - scope if pmax - scope > 0 else 1

        if not base_url:
            # default to current page url, and drop /listing path if any
            base_url = request.httprequest.path.split('/page')[0]

        qstring = keep_query()

        def get_url(page_nr):
            if page_nr <= 1:
                _url = base_url
            else:
                _url = "{}/page/{}".format(base_url, page_nr)
            if qstring:
                _url += '?' + qstring
            return _url

        if url_getter is None:
            url_getter = get_url

        page_prev = max(pmin, page - 1)
        page_next = min(pmax, page + 1)
        prev_url = url_getter(page_prev)
        next_url = url_getter(page_next)
        last_url = url_getter(pmax)
        paginated = AttrDict({
            "items_count": total,
            "need_nav": page_count > 1,
            "page_count": page_count,
            "has_prev": page > pmin,
            "has_next": page < pmax,
            "current": AttrDict({
                'url': url_getter(page),
                'num': page,
            }),
            "page_prev": AttrDict({
                'url': prev_url,
                'num': page_prev,
            }),
            "page_next": AttrDict({
                'url': next_url,
                'num': page_next,
            }),
            "page_last": AttrDict({
                'url': last_url,
                'num': pmax,
            }),
            "pages": [
                AttrDict({'url': url_getter(i), 'num': i})
                for i in xrange(pmin, pmax + 1)
            ]
        })
        return paginated

    def paginate(self, all_items, page=1, step=10):
        """Prepare pagination."""
        total = len(all_items)
        start = (page and page - 1) or 0
        step = step or 10
        items = all_items[start * step: (start * step) + step]
        paginated = self.pager(total, page=page, step=step)
        paginated['results'] = items
        return paginated

    def get_paginated_listing(self, page=0, step=10, **kw):
        """Get items for listing sliced for pagination."""
        all_items = self.get_listing(**kw)
        return self.paginate(all_items, page=page, step=step)

    def get_paginated_media_listing(self, page=0, step=10, **kw):
        """Get items for listing sliced for pagination."""
        # XXX: shoul we merge this w/ above listing?
        all_items = self.get_media_listing(**kw)
        return self.paginate(all_items, page=page, step=step)

    @api.model
    def get_media_listing(self, published=True,
                          category=None, order=None,
                          item=None, path=None,
                          lang=None):
        """Return items to be listed.

        Tweak filtering by:

        `published` to show published/unpublished items or both
        `category` a category obj to limit listing to specific category
        `lang` a lang obj or lang code to limit listing to specific language
        `order` to override ordering by sequence

        # XXX: should we provide a path for media too?
        `path` to search in a specific path instead of
        just listing current item's children.

        By default filter w/ `list_types_ids` if valued.
        """
        item = item or self
        search_args = []
        if path is None:
            search_args.append(('res_id', '=', item.id))
        else:
            search_args.append(('path', '=like', path + '%'))

        # use specific `published` items but bypass it if manager
        if published is not None and \
                not self.env.user.has_group('website_cms.cms_manager'):
            search_args.append(('website_published', '=', published))

        if category is not None:
            search_args.append(('category_id', '=', category.id))

        if isinstance(lang, basestring):
            lang = self.env['res.lang'].search([('code', '=', lang)])

        if lang:
            search_args.append(('lang_id', '=', lang.id))

        order = order or 'sequence asc'
        media = self.env['cms.media'].search(
            search_args,
            order=order
        )
        return media

    @api.model
    def get_translations(self):
        """Return translations for this page."""
        return self._get_translations(page_id=self.id)

    @tools.ormcache('page_id')
    def _get_translations(self, page_id=None):
        """Return all available translations for a page.

        We assume that a page is translated when the name is.
        """
        query = """
            SELECT lang,value FROM ir_translation
            WHERE res_id={page_id}
            AND state='translated'
            AND type='model'
            AND name='cms.page,name'
        """.format(page_id=page_id)
        self.env.cr.execute(query)
        res = self.env.cr.fetchall()
        return dict(res)


class CMSPageType(models.Model):
    """Model of a CMS page type."""

    _name = 'cms.page.type'
    _description = 'CMS page type'

    name = fields.Char('Name', translate=True)
