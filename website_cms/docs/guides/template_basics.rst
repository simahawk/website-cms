.. _template_basics:

###############
Template basics
###############

The base module `website_cms` does not provide an theme for your CMS.
You are responsible for building your own theme and include basic snippets to add navigation, listings and so on.

The following is an overview on available templates and their usage.


Default page views
==================

Templates and views to be used to show page contents.
Likely all these views will serve as an example for your theme.


Default page content view
-------------------------

``website.page_default``: display page's HTML content only, title and description are hidden.

You can select it via backend as "Page default".


Default page content view with title and description
----------------------------------------------------

``website.page_default_with``: display page's title, description and HTML content.

All the fields are editable if in edit mode.

You can select it via backend as "Page default with title and descr".

Both ``page_default`` and ``page_default_with`` make use of a smaller template
called ``page_default_content`` that you can reuse in your views::

    <template id="page_default_with" name="Page default with title and descr">
        <t t-call="website.layout">
          <div class="container">
            <t t-call="website_cms.page_default_content">
              <t t-set="show_name" t-value="True" />
              <t t-set="show_description" t-value="True" />
            </t>
          </div>
        </t>
    </template>

The important part here is::

    <t t-call="website_cms.page_default_content">
        <t t-set="show_name" t-value="True" />
        <t t-set="show_description" t-value="True" />
    </t>

and is exactly the piece of snippet that you can use in your custom view.


Default page content view with listing
--------------------------------------

``website.page_default_listing``: display page's title, description, HTML content and a bare listing of contents below.

All the fields are editable if in edit mode and all the sub-pages contained in the current one will be displayed
with their preview image.

You can select it via backend as "Page default listing".


Include page information
========================

The views mentioned above use basic markup for including page's info.
Here is a brief summary.

Include title::

    <h1 id="object_name"
        t-field="main_object.name"
        t-att-contenteditable="editable and 'true' or None"
        />

Include description::

    <t t-if="main_object.description">
      <h2 id="object_description" class="description" t-field="main_object.description" />
    </t>

Include HTML content::

    <div id="object_body"
         t-field="main_object.body"
         class="oe_structure"
         t-att-contenteditable="editable and 'true' or None"
         />

Include preview image::

    <t t-set="preview_url" t-value="website.safe_image_url(item, 'image_thumb')" />
    <t t-if="preview_url">
        <img class="item-preview"
             t-att-src="preview_url"
             t-att-alt="item.description or item.name" />
    </t>

Include basic listing::

    <t t-set="listing_items" t-value="main_object.get_listing()" />
    <t t-foreach="listing_items" t-as="item">
        <li>
            <a class="item-link"
               t-att-title="item.description or item.name"
               t-att-href="item.website_url">
                <span t-field="item.name" />
            </a>
        </li>
    </t>

Include pills navigation, horizontal::

    <t t-call="website_cms.context_nav_horiz" />

or vertical::

    <t t-call="website_cms.context_nav_vert" />


.. note::

    Be aware that

    - controlling "contenteditable" attribute based on "editable" variable is done to avoid browsers to make the item editable without Odoo editor.



Management actions
------------------

If you want to show management actions (edit, publish/unpublish) in your view, you should include::

    <t t-call="website_cms.mgmt_actions" />

Note that this is already done by the template ``add_mgmt_actions``, which adds it above the ``<main />`` element of Odoo layout.
If you want to move it elsewhere you can disable it like this::

    <record id="website_cms.add_mgmt_actions" model="ir.ui.view">
        <field name="active" eval="0" />
    </record>


Status message
--------------

When performing an action like submitting an edit or create form of a page
you can add status message to show the status of the operation. You can add it like this::

    <t t-call="website_cms.status_message" />

The result looks like:

.. image:: status_msg.png

Note that this is already done by the template ``add_status_message``, which adds it above the ``<main />`` element of Odoo layout.
If you want to move it elsewhere you can disable it like this::

    <record id="website_cms.add_status_message" model="ir.ui.view">
        <field name="active" eval="0" />
    </record>


Debug info
----------

If you want to know more aboit the view you are currently using::

    <t t-call="website_cms.debug_view_info" />


.. warning:: this works only in debug mode


Create your own view
====================

A CMS view is just an Odoo template (``ir.ui.view`` model) with the flag ``cms_view`` on.

So, first you define the template as usual and then you activate it with 3 simple lines::

    <template id="page_default" name="Page default">
        <t t-call="website.layout">
        [...]
        </t>
    </template>

    <!-- enable view for cms -->
    <record id="website_cms.page_default" model="ir.ui.view">
        <field name="cms_view" eval="1" />
    </record>

Activating the flag is required to make the view appear among available cms views on the cms page.

The content of the template can be whatever you want and you can use one or more of the above mentioned templates into it.

In the template among other variables you have:

* ``main_object``: the current page instance
* ``parent``: the parent page if main object is child page
