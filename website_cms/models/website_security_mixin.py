"""Website mixins."""

# -*- coding: utf-8 -*-

# pylint: disable=E0401
# pylint: disable=W0212
# pylint: disable=R0903
# pylint: disable=R0201
# pylint: disable=R0913
# pylint: disable=R0914


from openerp import models
from openerp import fields
from openerp import api
from openerp.addons.website.models import ir_http
from openerp.http import request
from openerp import SUPERUSER_ID

from werkzeug.exceptions import NotFound


class WebsiteSecurityMixin(models.AbstractModel):
    """Provide basic logic for protecting website items.

    Features: TODO
    * `foo`
    * `bar`
    """

    _name = "website.security.mixin"
    _description = "A mixin for protecting website content"
    # admin groups that bypass security checks
    _admin_groups = (
        'base.group_website_publisher',
    )

    view_group_ids = fields.Many2many(
        string='View Groups',
        comodel_name='res.groups',
        help=(u"Restrict `view` access to this item to specific groups. "
              u"No group means anybody can see it.")
    )

    def _is_admin(self):
        for gid in self._admin_groups:
            if self.env.user.has_group(gid):
                return True
        return False

    def _check_user_groups(self, group_ids):
        """Check wheter current user matches given groups."""
        return any([x in self.env.user.groups_id._ids
                    for x in group_ids])

    def _bypass_check_permission(self):
        """Bypass checking permissions.

        Bypass if:

        * you are super-user
        * you are in a group listed in `_admin_groups`
        """
        if self._uid == SUPERUSER_ID:
            return True
        admin_groups = []
        for k in self._admin_groups:
            ref = self.env.ref(k)
            if ref:
                admin_groups.append(ref.id)
        return self._check_user_groups(admin_groups)

    @api.model
    def check_permission(self, obj=None, mode='view'):
        """Check permission on given object.

        @param `obj`: the item to check.
        If not `obj` is passed `self` will be used.

        @param `mode`: the permission mode to check.
        """
        obj = obj or self
        fname = mode + '_group_ids'

        if fname not in obj._model:
            # nothing to check here
            return True

        # obj comes w/ a temporary env,
        # w/ uid beeing an instance of ir_http.RequestUID
        # which is not suitable for std ORM operations.
        # Let's make sure we get the right user here!
        if request.session.uid:
            _obj = obj.with_env(self.env(user=request.session.uid))
        else:
            _obj = obj.with_env(request.env)

        if _obj._bypass_check_permission():
            return True
        if not _obj[fname]:
            # no groups, fine
            return True

        check1 = _obj._check_user_groups(_obj[fname]._ids)
        return check1

    @api.model
    def _search(self, args, offset=0, limit=None,
                order=None, count=False, access_rights_uid=None):
        """Implement security check based on `website_published`
        and `view_group_ids`.

        The goal is to hide items that current user cannot see
        in the frontend (like navigation, listings)
        and, why not, even in the backend.

        Here if we find a contraint on any group
        we filter out what the current user cannot view.

        Disclaimer: yes, we could use `ir.rule`s for this
        but since we want the end user to select a group
        easily without having to get in touch w/ rules,
        we chosed this way.

        To use `ir.rule` we'd need to extend them
        w/ a relation to real objects and put our hands
        inside rules computation, and keep user settings
        in sync with rules, etc, etc.
        The computation of the domain for a rule,
        applies only to groups associated to current user.
        We want the other way around: apply permission check
        to make sure that if a user does not belong
        to a specific group, he/she cannot see the item.
        Hence, you must define a global rule and add it
        a new field for a groups, and then mess around
        w/ domain computation.

        As of today, this is still a prototype
        and we might change/improve this check ;)

        Finally, the `SecureModelConverter` base klass
        is using `exists` to check if the item exists.
        This method in turns does not check for security.
        Hence, we are trying to use the same mechanism
        for both cases.
        """
        # if no editing rights, hide not published content
        published_filter = any(['website_published' in x for x in args])
        if not self._is_admin() and not published_filter:
            args.append(('website_published', '=', True))

        res = super(WebsiteSecurityMixin, self)._search(
            args, offset=offset, limit=limit, order=order,
            count=count, access_rights_uid=access_rights_uid
        )
        if 'view_group_ids' not in self._model:
            return res

        if self._bypass_check_permission():
            return res

        # retrieve relation params
        view_field = self._model._fields['view_group_ids']
        relation = view_field.relation
        ob_col = view_field.column1
        group_col = view_field.column2

        # search for all mapping w/ groups
        query = (
            "SELECT {ob_col}, array_agg({group_col}) "
            "FROM {relation} "
            "GROUP BY {ob_col}"
        ).format(ob_col=ob_col,
                 relation=relation,
                 group_col=group_col)
        self.env.cr.execute(query)
        tocheck = self.env.cr.fetchall()

        # finally exclude all the ids
        # that do not match user's group
        for oid, group_ids in tocheck:
            if isinstance(res, list) and oid not in res\
                    or isinstance(res, (int, long)) and oid != res:
                continue
            if not self._check_user_groups(group_ids):
                res.remove(oid)
        return res


class SecureModelConverter(ir_http.ModelConverter):
    """A new model converter w/ security check.

    The base model converter is responsible of
    converting a slug to a real browse object.

    We want to intercept this on demand and apply security check,
    so that whichever model exposes `website.security.mixin`
    capabilities and uses this route converter,
    will be protected based on mixin behaviors.

    You can use it like this:

        @http.route(['/foo/<secure_model("my.model"):main_object>'])
    """

    def to_python(self, value):
        """Get python record and check it.

        If no permission here, just raise a NotFound!
        """
        record = super(SecureModelConverter, self).to_python(value)
        if isinstance(record, WebsiteSecurityMixin) \
                and not record.check_permission(mode='view'):
            raise NotFound()
        return record


class IRHTTP(models.AbstractModel):
    """Override to add our model converter.

    The new model converter make sure to apply security checks.

    See `website.models.ir_http` for default implementation.
    """

    _inherit = 'ir.http'

    def _get_converters(self):
        return dict(
            super(IRHTTP, self)._get_converters(),
            secure_model=SecureModelConverter,
        )
