# -*- coding: utf-8 -*-

import base64
import json

from openerp import http
from openerp.http import request
import werkzeug
from werkzeug.exceptions import Forbidden
from openerp.tools.translate import _


from .main import ContextAwareMixin


class PageFormMixin(ContextAwareMixin):
    """CMS page Form controller."""

    form_name = ''
    form_title = ''
    form_mode = ''
    form_fields = ('name', 'description', 'tag_ids', )
    form_file_fields = ('image', )
    action_status = 'success'
    status_message_success = ''

    def get_template(self, main_object, **kw):
        """Override to force template."""
        return self.template

    def get_render_values(self, main_object, parent=None, **kw):
        """Override to preload values."""
        _super = super(PageFormMixin, self)
        values = _super.get_render_values(main_object, **kw)

        base_url = '/cms'
        if main_object:
            base_url = main_object.website_url

        name = request.params.get('name') or kw.get('name')
        values.update({
            'name': name,
            'form_action': base_url + '/' + self.form_name,
        })

        values.update(self.load_defaults(main_object, **kw))

        # make sure we do not allow website builder Form
        values['editable'] = values['translatable'] = False
        # XXX: we should handle this
        # values['errors'] = []
        # values['status_message'] = ''
        values['view'] = self
        values['cms_form_mode'] = self.form_mode
        return values

    def load_defaults(self, main_object, **kw):
        """Override to load default values."""
        defaults = {}
        if not main_object:
            return defaults
        for fname in self.form_fields:
            value = getattr(main_object, fname)
            custom_handler = getattr(self, '_load_default_' + fname, None)
            if custom_handler:
                value = custom_handler(main_object, value, **kw)
            defaults[fname] = value

        for fname in self.form_file_fields:
            defaults['has_' + fname] = bool(getattr(main_object, fname))
        return defaults

    def _load_default_tag_ids(self, main_object, value, **kw):
        tags = [dict(id=tag.id, name=tag.name) for tag in value]
        return json.dumps(tags)

    def extract_values(self, request, main_object, **kw):
        """Override to manipulate POST values."""
        # TODO: sanitize user input and add validation!
        errors = []
        values = {}
        valid_fields = self.form_fields + self.form_file_fields
        form_values = {
            k: v for k, v in kw.iteritems()
            if k in valid_fields
        }
        for fname in valid_fields:
            value = form_values.get(fname)
            custom_handler = getattr(self, '_extract_' + fname, None)
            if custom_handler:
                value = custom_handler(value, errors, form_values)
            if fname in form_values:
                # a custom handler could pop a field
                # to discard it from submission, ie: keep an image as it is
                values[fname] = value
        return values, errors

    def _extract_image(self, field_value, errors, form_values):
        if form_values.get('keep_image') == 'yes':
            # prevent discarding image
            form_values.pop('image')
            return None
        if hasattr(field_value, 'read'):
            image_content = field_value.read()
            value = base64.encodestring(image_content)
        else:
            value = field_value.split(',')[-1]
        return value

    def _extract_tag_ids(self, field_value, errors, form_values):
        if field_value:
            return request.env['cms.tag']._tag_to_write_vals(tags=field_value)
        return None

    def add_status_message(self, status_message):
        """Inject status message in session."""
        try:
            request.session['status_message'].append(status_message)
        except KeyError:
            request.session['status_message'] = [status_message, ]

    def before_post_action(self, parent=None, main_object=None, **kw):
        """Perform actions before form handling."""
        # # cleanup status messages
        if 'status_message' in request.session:
            del request.session['status_message']

    def after_post_action(self, parent=None, main_object=None, **kw):
        """Perform actions after form handling."""
        # add status message if any
        status_message = getattr(self,
                                 'status_message_' + self.action_status, None)
        if status_message:
            self.add_status_message(status_message)

    # def get_fields(self, writable_fields):
    #     authorized = request.env['ir.model'].search(
    #         [('model', '=', self.model)]).get_authorized_fields()
    #     return [
    #         self.prepare_field(x) for x in authorized
    #         if x in writable_fields
    #     ]

    # def prepare_field(self, field_info):
    #     return field_info


class CreatePage(http.Controller, PageFormMixin):
    """CMS page create controller."""

    form_name = 'add-page'
    form_title = _('Add page')
    form_mode = 'create'
    template = 'website_cms.page_form'
    status_message_success = {
        'type': 'info',
        'title': 'Info:',
        'msg': _(u'Page created.'),
    }

    def load_defaults(self, main_object, **kw):
        """Override to preload values."""
        defaults = {}
        if main_object:
            defaults['parent_id'] = main_object.id
            defaults['form_action'] = \
                main_object.website_url + '/' + self.form_name
            for fname in ('type_id', 'view_id'):
                fvalue = getattr(main_object, 'sub_page_' + fname)
                defaults[fname] = fvalue and fvalue.id or False

        return defaults

    @http.route([
        '/cms/add-page',
        '/cms/<secure_model("cms.page"):parent>/add-page',
        '/cms/<path:path>/<secure_model("cms.page"):parent>/add-page',
    ], type='http', auth='user', methods=['GET', 'POST'], website=True)
    def add(self, parent=None, **kw):
        """Handle page add view and form submit."""
        if request.httprequest.method == 'GET':
            return self.render(parent, **kw)

        elif request.httprequest.method == 'POST':
            self.before_post_action(parent=parent, **kw)
            # handle form submission
            values = self.load_defaults(parent, **kw)
            # TODO: handle errors
            _values, errors = self.extract_values(request, parent, **kw)
            values.update(_values)
            new_page = request.env['cms.page'].create(values)
            url = new_page.website_url + '?enable_editor=1'
            self.after_post_action(main_object=new_page, **kw)
            return werkzeug.utils.redirect(url)

    def after_post_action(self, parent=None, main_object=None, **kw):
        """Add extra msg in case description is missing."""
        super(CreatePage, self).after_post_action()
        if not main_object.description:
            msg = {
                'type': 'warning',
                'title': 'Note:',
                'msg': _(u'No description for this page yet. '
                         u'You see this because you can edit this page. '
                         u'A brief description can be useful '
                         u'to show a summary of this content '
                         u'in many views (like listing or homepage).'),
            }
            self.add_status_message(msg)


class EditPage(http.Controller, PageFormMixin):
    """CMS page edit controller."""

    form_name = 'edit-page'
    form_title = _('Edit page')
    form_mode = 'write'
    template = 'website_cms.page_form'
    status_message_success = {
        'type': 'info',
        'title': 'Info:',
        'msg': _(u'Page updated.'),
    }

    def _check_security(self, main_object):
        if request.website and \
                not request.website.cms_can_edit(main_object):
            raise Forbidden(_(u'You are not allowed to edit this page!'))

    @http.route([
        '/cms/<secure_model("cms.page"):main_object>/edit-page',
        '/cms/<path:path>/<secure_model("cms.page"):main_object>/edit-page',
    ], type='http', auth='user', methods=['GET', 'POST'], website=True)
    def edit(self, main_object, **kw):
        """Handle page edit view and form submit."""
        if request.httprequest.method == 'GET':
            # render form
            return self.render(main_object, **kw)
        elif request.httprequest.method == 'POST':
            self._check_security(main_object)
            self.before_post_action(main_object=main_object, **kw)
            # handle form submission
            # TODO: handle errors
            values, errors = self.extract_values(request, main_object, **kw)
            main_object.write(values)
            self.after_post_action(main_object=main_object, **kw)
            return http.local_redirect(main_object.website_url)

    def after_post_action(self, parent=None, main_object=None, **kw):
        """Add extra msg in case description is missing."""
        super(EditPage, self).after_post_action()
        if not main_object.description:
            msg = {
                'type': 'warning',
                'title': 'Note:',
                'msg': _(u'No description for this page yet. '
                         u'You see this because you can edit this page. '
                         u'A brief description can be useful '
                         u'to show a summary of this content '
                         u'in many views (like listing or homepage).'),
            }
            self.add_status_message(msg)
