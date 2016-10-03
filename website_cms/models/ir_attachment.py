# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import itertools

from openerp import models
from openerp import SUPERUSER_ID


class IRAttachment(models.Model):
    """Fix attachment search.

    `cms.media` inherit from `ir.attachment`
    so the table model for searches is not `ir_attachment`
    but `cms_media`. See `FIX THIS QUERY` line.

    Yes, we need to submit a patch + PR for this ;)

    https://github.com/odoo/odoo/blob/9.0/openerp/addons/base/ir/ir_attachment.py#L339
    """

    _inherit = 'ir.attachment'

    def _search(self, cr, uid, args, offset=0, limit=None, order=None,
                context=None, count=False, access_rights_uid=None):
        # add res_field=False in domain if not present; the arg[0] trick below
        # works for domain items and '&'/'|'/'!' operators too
        if not any(arg[0] in ('id', 'res_field') for arg in args):
            args.insert(0, ('res_field', '=', False))

        ids = models.Model._search(self, cr, uid, args, offset=offset,
                                   limit=limit, order=order,
                                   context=context, count=False,
                                   access_rights_uid=access_rights_uid)
        if uid == SUPERUSER_ID:
            # rules do not apply for the superuser
            return len(ids) if count else ids

        if not ids:
            return 0 if count else []

        # Work with a set, as list.remove() is prohibitive for large lists of documents
        # (takes 20+ seconds on a db with 100k docs during search_count()!)
        orig_ids = ids
        ids = set(ids)

        # For attachments, the permissions of the document they are attached to
        # apply, so we must remove attachments for which the user cannot access
        # the linked document.
        # Use pure SQL rather than read() as it is about 50% faster
        # for large dbs (100k+ docs),
        # and the permissions are checked in super() and below anyway.

        # FIX THIS QUERY TO MAKE IT WORK
        # W/ MODELS THAT INHERITS FROM ir.attachments
        query = """SELECT id, res_model, res_id, public
        FROM {} WHERE id = ANY(%s)""".format(self._table)
        cr.execute(query, (list(ids),))
        targets = cr.dictfetchall()
        model_attachments = {}
        for target_dict in targets:
            if not target_dict['res_model'] or target_dict['public']:
                continue
            # model_attachments = { 'model': { 'res_id': [id1,id2] } }
            model_attachments.setdefault(
                target_dict['res_model'], {}).setdefault(
                    target_dict['res_id'] or 0, set()).add(target_dict['id'])

        # To avoid multiple queries for each attachment found, checks are
        # performed in batch as much as possible.
        ima = self.pool.get('ir.model.access')
        for model, targets in model_attachments.iteritems():
            if model not in self.pool:
                continue
            if not ima.check(cr, uid, model, 'read', False):
                # remove all corresponding attachment ids
                for attach_id in itertools.chain(*targets.values()):
                    ids.remove(attach_id)
                continue # skip ir.rule processing, these ones are out already

            # filter ids according to what access rules permit
            target_ids = targets.keys()
            allowed_ids = [0] + self.pool[model].search(
                cr, uid, [('id', 'in', target_ids)], context=context)
            disallowed_ids = set(target_ids).difference(allowed_ids)
            for res_id in disallowed_ids:
                for attach_id in targets[res_id]:
                    ids.remove(attach_id)

        # sort result according to the original sort ordering
        result = [id for id in orig_ids if id in ids]
        return len(result) if count else list(result)
