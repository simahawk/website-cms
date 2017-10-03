# -*- coding: utf-8 -*-

from openerp import http
# from openerp.tools.translate import _
from openerp.http import request


class SearchView(http.Controller):
    """Controller for search view."""

    _results_per_page = 10
    _min_search_len = 3
    _case_sensitive = False

    template = 'website_cms_search.page_search'

    @http.route([
        '/cms/search',
        '/cms/search/page/<int:page>',
    ], type='http', auth="public", website=True)
    def search(self, page=1, **kw):
        """Search CMS pages."""
        values = {
            'has_results': False,
            'paginated': {},
            'min_search_len_ok': True,
            'min_search_len': self._min_search_len,
        }
        search_text = kw.get('search_text', '')
        if len(search_text) < self._min_search_len:
            values['min_search_len_ok'] = False
        else:
            pages = self._search(search_text)
            values['has_results'] = bool(pages)
            page_model = request.env['cms.page']
            values['paginated'] = page_model.paginate(
                pages,
                page=page,
                step=self._results_per_page)
        return request.render(self.template, values)

    def _get_query(self, lang, case_sensitive=False):
        """Build sql query."""
        is_default_lang = lang == request.website.default_lang_code
        if is_default_lang:
            sql_query = """
                SELECT id
                FROM cms_page
                WHERE
                    name {like} %s
                    OR description {like} %s
                    OR body {like} %s
            """
        else:
            sql_query = """
                  SELECT p.id
                  FROM cms_page p, ir_translation tr
                  WHERE
                    tr.type='model'
                    AND tr.lang='{}'
                    AND tr.res_id=p.id
                    AND tr.name like 'cms.page,%%'
                    AND tr.state='translated'
            """.format(lang)
            if case_sensitive:
                sql_query += """ AND tr.value {like} %s"""
            else:
                sql_query += """ AND lower(tr.value) {like} %s"""
        like = case_sensitive and 'like' or 'ilike'
        return sql_query.format(like=like)

    def _search(self, search_text):
        """Do search."""
        lang = request.context.get('lang')
        order = 'published_date desc'
        case_sensitive = self._case_sensitive
        sql_query = self._get_query(lang, case_sensitive=case_sensitive)
        params = ['%{}%'.format(search_text)
                  for x in xrange(sql_query.count('%s'))]
        request.env.cr.execute(sql_query, params)
        res = request.env.cr.fetchall()
        page_ids = tuple(set([x[0] for x in res]))

        # limit = self._results_per_page
        # offset = (page - 1) * self._results_per_page

        page_model = request.env['cms.page']
        search_args = [
            ('id', 'in', page_ids),
        ]
        pages = page_model.search(search_args,
                                  order=order)
        return pages
