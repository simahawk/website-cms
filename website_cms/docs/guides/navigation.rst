.. _navigation:

##########
Navigation
##########

Build your own nav menu
=======================

The CMS page has a `Nav include` flag. When this flag is on the item will be included in the main navigation listing.

.. warning::
    You won't find a ready-to-use menu into ``website_cms`` since its main goal is to give you the tool to do it yourself as you prefer.

    So, the following is just an example on how you can generate a main menu for your website.

To get nav pages, just use the method ``website.get_nav_pages``. This method returns a hierarchical list of items ordered by position (``sequence`` field), in which every item (or sub item) as the following schema::

    item = AttrDict({
        'id': item.id,  # database id of the page
        'name': item.name,  # name of the page
        'url': item.website_url,  # public url of the page
        'children': children,  # list of children pages
        'website_published': item.website_published,  # published/private page
    })


Knowing this, your menu's template could look like:

.. code-block:: xml

    <template id="main_nav">

      <ul class="nav navbar-nav">
        <t t-foreach="website.get_nav_pages(max_depth=4)" t-as="item">

          <li t-attf-class="nav-item #{item_first and 'active' or ''}">

            <a t-att-href="item.url" t-esc="item.name">Page title</a>

            <t t-if="item.children">
              <div class="submenu-content">
                <t t-foreach="item.children" t-as="sub">
                  <ol>
                    <li class="nav-sub-item">
                      <a t-att-href="sub.url">
                        <span t-esc="sub.name">Sub page title</span>
                      </a>
                    </li>
                    <t t-foreach="sub.children" t-as="subsub">
                      <li>
                        <a t-att-href="subsub.url">
                          <span t-esc="subsub.name">Sub sub page title</span>
                        </a>
                      </li>
                    </t>
                  </ol>
                </t>
              </div>
            </t>

          </li>

        </t>
      </ul>

    </template>

In this case, by passing ``max_depth=4``, we are generating a 4 levels hierarchy, but you can lower that value according to your needs.

These are the parameters you can use to customize you nav:

* ``max_depth`` to set menu levels, default: 3;
* ``publish`` to filter public state, possible values:
    * ``None`` all pages;
    * ``True`` all published pages (default);
    * ``False`` all private pages;
* ``nav`` to filter on "Nav include" flag, possible values:
    * ``None`` all pages;
    * ``True`` all nav-included pages (default);
    * ``False`` all not nav-included pages;
* ``type_ids`` to filter pages by a list of types' ids, default to ``website_cms.default_page_type`` id.


