# -*- coding: utf-8 -*-

# pylint: disable=E0401
# pylint: disable=W0212
from openerp import models
from openerp import fields
from openerp import api
# from openerp.tools.translate import _
from openerp.addons.website.models.website import slug

from openerp.addons.website_cms.utils import IMAGE_TYPES
from openerp.addons.website_cms.utils import VIDEO_TYPES
from openerp.addons.website_cms.utils import AUDIO_TYPES
from openerp.addons.website_cms.utils import download_image_from_url
from openerp.addons.website_cms.utils import guess_mimetype
from openerp.addons.website_cms.utils import AttrDict

import urlparse


# XXX: we should move this stuff to website_cms
# and use services like http://noembed.com
EMBED_PATTERN = AttrDict({
    'youtube': AttrDict({
        'key': 'v',
        'url': 'https://www.youtube.com/embed/{vid}',
    }),
})
IMAGE_PREVIEW_PATTERN = AttrDict({
    'youtube': AttrDict({
        'key': 'v',
        'url': 'https://i.ytimg.com/vi/{vid}/hqdefault.jpg',
    }),
})


def to_embed_url(url, provider='youtube'):
    """Simple function to convert video url to embed url.

    Example:

        >>> to_embed_url('https://www.youtube.com/watch?v=Z5cterm_nW0')
        https://www.youtube.com/embed/Z5cterm_nW0

    The best would be to make use of services like `oembed`
    but we are taking this easy at the moment ;)
    """
    pattern = EMBED_PATTERN.get(provider)
    parsed = urlparse.urlparse(url)
    qstring = urlparse.parse_qs(parsed.query)
    if pattern and pattern.key in qstring:
        return pattern.url.format(vid=qstring[pattern.key][0])
    return url


def to_preview_url(url, provider='youtube'):
    """Simple function to convert video url to image preview url.

    Example:

        >>> to_preview_url('https://www.youtube.com/watch?v=Z5cterm_nW0')
        https://i.ytimg.com/vi/Z5cterm_nW0/hqdefault.jpg

    The best would be to make use of services like `oembed`
    but we are taking this easy at the moment ;)
    """
    pattern = IMAGE_PREVIEW_PATTERN.get(provider)
    parsed = urlparse.urlparse(url)
    qstring = urlparse.parse_qs(parsed.query)
    if pattern and pattern.key in qstring:
        return pattern.url.format(vid=qstring[pattern.key][0])
    return url


class CMSMedia(models.Model):
    """Model of a CMS media."""

    _name = 'cms.media'
    _description = 'CMS Media'
    _order = 'sequence, id'
    _inherit = ['ir.attachment',
                'website.published.mixin',
                'website.orderable.mixin',
                'website.coremetadata.mixin',
                'website.image.mixin',
                'website.security.mixin']

    name = fields.Char(
        'Name',
        required=True,
        translate=True,
    )
    description = fields.Text(
        'Description',
        translate=True,
    )
    lang_id = fields.Many2one(
        string='Language',
        comodel_name='res.lang',
        domain=lambda self: self._domain_lang_id(),
        select=True,
    )
    page_id = fields.Many2one(
        string='Page',
        comodel_name='cms.page',
    )
    category_id = fields.Many2one(
        string='Category',
        comodel_name='cms.media.category',
        compute='_compute_category_id',
        store=True,
        readonly=True,
    )
    force_category_id = fields.Many2one(
        string='Force category',
        comodel_name='cms.media.category',
        domain=[('active', '=', True)],
    )
    icon = fields.Char(
        'Icon',
        compute='_compute_icon',
        readonly=True,
    )
    website_url = fields.Char(
        'Website URL',
        compute='_website_url',
        readonly=True,
    )

    @api.model
    def _domain_lang_id(self):
        """Return options for lang."""
        try:
            website = self.env['website'].get_current_website()
        except RuntimeError:
            # *** RuntimeError: object unbound
            website = None
        if website:
            languages = website.language_ids
        else:
            languages = self.env['res.lang'].search([])
        return [('id', 'in', languages.ids)]

    @api.multi
    @api.depends('force_category_id', 'mimetype', 'url')
    def _compute_category_id(self):
        """Compute media category."""
        default = self.env.ref('website_cms.media_category_document')
        for item in self:
            if item.force_category_id:
                item.category_id = item.force_category_id
                continue
            else:
                guessed = self.guess_category(item.mimetype)
                if guessed:
                    item.category_id = guessed
                    continue
            item.category_id = default

    def guess_category(self, mimetype):
        """Guess media category by mimetype."""
        xmlid = None
        # look for real media first
        if mimetype in IMAGE_TYPES:
            xmlid = 'website_cms.media_category_image'
        if mimetype in VIDEO_TYPES:
            xmlid = 'website_cms.media_category_video'
        if mimetype in AUDIO_TYPES:
            xmlid = 'website_cms.media_category_audio'
        if xmlid:
            return self.env.ref(xmlid)
        # fallback to search by mimetype
        category_model = self.env['cms.media.category']
        cat = category_model.search([
            ('mimetypes', '=like', '%{}%'.format(mimetype)),
            ('active', '=', True)
        ])
        return cat and cat[0] or None

    @api.multi
    @api.depends('category_id', 'mimetype', 'url')
    def _compute_icon(self):
        """Compute media icon."""
        for item in self:
            item.icon = item.get_icon()

    @api.model
    def get_icon(self, mimetype=None):
        """Return a CSS class for icon.

        You can override this to provide different
        icons for your media.
        """
        # TODO: improve this default
        # maybe using the same icon from media category (?)
        return 'fa fa-file-o'

    @api.multi
    def _website_url(self):
        """Override method defined by `website.published.mixin`."""
        url_pattern = '/web/content/{model}/{ob_id}/{field_name}/{filename}'
        for item in self:
            url = item.url
            if not url:
                url = url_pattern.format(
                    model=item._name,
                    ob_id=item.id,
                    field_name='datas',
                    filename=item.datas_fname or 'download',
                )
            item.website_url = url

    @api.multi
    def update_published(self):
        """Publish / Unpublish this page right away."""
        self.write({'website_published': not self.website_published})

    @api.model
    def create(self, vals):
        """Override to keep link w/ page resource and handle url.

        `ir.attachment` have a weak relation w/ related resources.
        We want the user to be able to select a page,
        but on the same time we need to keep this in sync w/
        attachment machinery. There you go!
        """
        if vals.get('page_id') is not None:
            vals['res_id'] = vals.get('page_id')
            vals['res_model'] = vals.get('page_id') and 'cms.page'
        # TODO: use noembed service
        url = vals.get('url')
        if url and 'youtube' in url:
            vals['url'] = to_embed_url(url)
        return super(CMSMedia, self).create(vals)

    @api.multi
    def write(self, vals):
        """Override to keep link w/ page resource."""
        if vals.get('page_id') is not None:
            vals['res_id'] = vals.get('page_id')
            vals['res_model'] = vals.get('page_id') and 'cms.page'
        # TODO: use noembed service
        url = vals.get('url')
        if url and 'youtube' in url:
            vals['url'] = to_embed_url(url)
        return super(CMSMedia, self).write(vals)

    @api.model
    def is_image(self, mimetype=None):
        """Whether this is an image."""
        mimetype = mimetype or self.mimetype
        if mimetype:
            return mimetype in IMAGE_TYPES
        # mimetype is computed on create
        if self.url:
            return guess_mimetype(self.url) in IMAGE_TYPES

    @api.model
    def is_video(self):
        """Whether this is a video."""
        return self.mimetype in VIDEO_TYPES

    # TODO: we should use services like http://noembed.com
    @api.multi
    @api.onchange('url', 'datas')
    def _preload_preview_image(self):
        """Preload preview image based on url and mimetype."""
        for item in self:
            # use _compute_mimetype from ir.attachment
            # that unfortunately is used only on create
            values = {}
            for fname in ('datas_fname', 'url', 'datas'):
                values[fname] = getattr(item, fname)
            item.mimetype = self._compute_mimetype(values)

            if item.is_image():
                if item.url:
                    image_content = download_image_from_url(item.url)
                else:
                    image_content = item.datas
                item.image = image_content
            if item.url and 'youtube' in item.url:
                image_content = download_image_from_url(
                    to_preview_url(item.url))
                item.image = image_content


class CMSMediaCategory(models.Model):
    """Model of a CMS media category."""

    _name = 'cms.media.category'
    _inherit = 'website.orderable.mixin'
    _description = 'CMS Media Category'

    name = fields.Char(
        'Name',
        required=True,
        translate=True,
    )
    mimetypes = fields.Text(
        'Mimetypes',
        help=('Customize mimetypes associated '
              'to this category.')
    )
    icon = fields.Char(
        'Icon',
    )
    active = fields.Boolean('Active?', default=True)

    @api.model
    def public_slug(self):
        """Used to generate relative URL for category."""
        return slug(self)
