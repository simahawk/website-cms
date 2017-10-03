.. _code-overview:

#############
Code Overview
#############

Here is an overview of models and their behavior.


********
CMS Page
********

:py:class:`~website_cms.models.cms_page.CMSPage` is the main protagonist of this system. It's the object that you use to create website contents and organize it hierarchically.

A page can contain other pages and media. You can assign a view to it an you can preset default values for contained pages (view and type).

The visual content of the page depends on the view: if the view exposes its html body (like the default one), then when you open the page in frontend you will see the html body rendered and you can edit it via website builder.

If the view is a listing view (like the default listing view) you won't see the html content but you'll see the listing of the sub pages.

Overall this means that the page behavior and content is indipendent from its presentation.

Fields
======

Main fields
-----------

* ``name`` is the title of the page. Used for slug generation.
* ``description`` is a short summary of the content. Useful for listings, search results, etc
* ``body`` contains the HTML content of the page (what you edit via website builder)
* ``parent_id`` m2o to parent page
* ``children_ids`` o2m to children pages
* ``media_ids`` o2m to `cms.media` objects
* ``type_id`` m2o to `cms.page.type` object. You can filter pages or use different views based on it. Defaults to `website_cms.default_page_type`.
* ``view_id`` m2o to `ir.ui.view` object. This is the view that is used to display the page.
* ``sub_page_type_id`` m2o to `cms.page.type` object. Set default page type for children pages. You can use this to pre-configure a website section behavior.
* ``sub_page_view_id`` m2o to `ir.ui.view` object. Set default page view for children pages. You can use this to pre-configure a website section look an feel.
* ``list_types_ids`` m2m to `cms.page.type`. Useful to force listed page types.
* ``nav_include`` whether to include or not the page into main navigation building (see ``website.get_nav_pages``).
* ``path`` is a computed field that matches the hierarchy of a page (eg: /A/B/C).

Helper methods
==============

Get the root page
-----------------

The root page is the upper anchestor of a hierarchy of pages.

.. code-block:: python

    >>> page.get_root()


List sub pages
---------------

A page can contain pages, this is how you can list them.

.. code-block:: python

    >>> page.get_listing()

By default it:

* order by sequence (position inside the parent)
* include only published items, unless you are into `website_cms.cms_manager` group
* if `page.list_types_ids` is valued it returns only sub pages matching that types

To learn how to tweak filtering take a look at :doc:`advanced_listing` section.


Mixins and extra features
=========================

The CMS page model rely on several mixins. Namely:

``website.seo.metadata``
    Standard from `web` module. Provides metadata for SEO tuning.

``website.published.mixin``
    Standard from `web` module. Provides basic publishing features.

``website.image.mixin`` (needs improvements)
    New from `website_cms`. Provides image the following image fields:
        * ``image`` full size image
        * ``image_medium`` medium size image
        * ``image_thumb`` thumb size image

``website.orderable.mixin``
    New from `website_cms`. Provides ``sequence`` field used to sort pages.

``website.coremetadata.mixin``
    New from `website_cms`. Provides core metadata.
    Exposes core fields:
    * ``create_date``
    * ``create_uid``
    * ``write_date``
    * ``write_uid``
    Adds extra fields:
    * ``published_date``
    * ``published_uid``

``website.security.mixin``
    New from `website_cms`. Provides per-content security control.
    By using the field ``view_group_ids`` you can decide which group can view the page.
    View permission per-user and edit permission are missing as of today.
    See :doc:`permissions` for further info.

``website.redirect.mixin``
    New from `website_cms`. Provides ability to make a page redirect to another CMS page, an Odoo page (`ir.ui.view` item with `page=True`) or an external link.
    See :doc:`redirects` for further info.


*********
CMS Media
*********

:py:class:`~website_cms.models.cms_media.CMSMedia` is an extension of Odoo attachments.

A media can be whatever file you want or an URL pointing to whatever web resource you want.

You can add media to a page from the quick link in the page backend view or from the media menu by selecting the page you want to assign the media to.

If you assign it to a page, you will be able to list all the media of that page easily.
A typical use case is a gallery: you could create a page "Gallery" and then you could add all the images as media into it.

Unlike attachments a media:

* can be published/unpublished indipendently from its related resource;
* is auto-categorized based on its mimetype (see `CMS Media Category`_ section);
* can be categorized manually;
* has a preview image
* automatically loads preview images from uploaded images, linked images, youtube videos.

Fields
======

Main fields
-----------

* ``name`` is the title of the media. Used for slug generation;
* ``description`` is a short summary of the content. Useful for listings, search results, etc;
* ``page_id`` m2o to a page;
* ``category_id`` m2o to `cms.media.category`, populated automatically;
* ``force_category_id`` m2o to `cms.media.category`, to be populated manually;
* ``lang_id`` m2o to `res.lang` model (for filtering media by language);
* ``icon`` a text field that should contain a css class for fontawesome (or services alike) that can be used to present the media in small listing etc.


Helper methods
==============

Is an image?
------------

Determine if the media is an image by checking its mimetype.

.. code-block:: python

    >>> media.is_image()

Is a video?
-----------

Determine if the media is a video by checking its mimetype.

.. code-block:: python

    >>> media.is_video()

Mixins and extra features
=========================

The CMS media model rely on several mixins. Namely:

``ir.attachment``
    Well, not a real mixin but it inherits all the standard ir.attachment features.

``website.published.mixin``
    Standard from `web` module. Provides basic publishing features.

``website.image.mixin`` (needs improvements)
    New from `website_cms`. Provides image the following image fields:
        * ``image`` full size image
        * ``image_medium`` medium size image
        * ``image_thumb`` thumb size image

``website.orderable.mixin``
    New from `website_cms`. Provides ``sequence`` field used to sort pages.

``website.coremetadata.mixin``
    New from `website_cms`. Provides core metadata.
    Exposes core fields:

        * ``create_date``
        * ``create_uid``
        * ``write_date``
        * ``write_uid``

    Adds extra fields:

        * ``published_date``
        * ``published_uid``

``website.security.mixin``
    New from `website_cms`. Provides per-content security control.
    By using the field ``view_group_ids`` you can decide which group can view the page.
    View permission per-user and edit permission are missing as of today.
    See :doc:`permissions` for further info.


******************
CMS Media Category
******************

:py:class:`~website_cms.models.cms_media.CMSMediaCategory` rappresent a media category.

You can use media categories to categorize your media.
By default a media is auto-categorized by its mimetype.

On each media category you can configure which mimetypes correspond to it.
For instance, the generic media category "Document" is defined as::

    <record id="media_category_document" model="cms.media.category">
        <field name="name">Document</field>
        <field name="icon">fa fa-file-o</field>
        <field name="mimetypes">
    text/plain
    application/pdf
    application/msword
    application/vnd.openxmlformats-officedocument.wordprocessingml.document
    application/vnd.ms-powerpointtd
    application/vnd.openxmlformats-officedocument.presentationml.slideshow
    application/vnd.openxmlformats-officedocument.presentationml.presentation
        </field>
    </record>

All the media matching one of the mimetypes described here will be automatically categorized as "Document".

.. note:: As of today images and videos are forced to match image and video category.

.. note:: You can always override auto-categorization by forcing the category on the media itself.

Fields
======

Main fields
-----------

* ``name`` is the title of the category. Used for slug generation;
* ``mimetypes`` multiline text field where to configure matching mimetypes;
* ``icon`` a text field that should contain a css class for fontawesome (or services alike) that can be used to present the category in small listing, filtering, etc;
* ``active`` you may want to show/hide categories when needed. You can use this field to filter which categories to show to your public without having to delete them.


Mixins and extra features
=========================

The CMS category model rely on several mixins. Namely:

``website.orderable.mixin``
    New from `website_cms`. Provides ``sequence`` field used to sort pages.
