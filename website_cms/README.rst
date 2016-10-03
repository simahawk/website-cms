.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License

Website CMS
===========

This is a module that adds real CMS features to your Odoo website.

Documentation: TODO

Premise
-------

Odoo has no real "Content Management System" features.
You cannot manage contents, since - beside blogs and blogposts - you don't have any real "web content".
You can design nice pages on the fly using the website builder - which is indeed a powerful and awesome feature -
but that's not the only thing a CMS should be able to do.

Yes, you have "pages" but right now an Odoo page is just a template
with some specific characteristics (flags, and so on) plus a fixed route "/page".
So, every page's URL in the website will be something like "/page/my-nice-article-about-something".
The same goes for blogs and blogposts: you will always have URLs like "/blog/my-nice-blog-1/posts/my-interesting-post-1".

With this limitations you cannot organize contents (a page, an attachment, etc) in sections and sub sections,
hence you cannot build a hierarchy that will allow to expose contents in a meaningful way, for you and your visitors.

The goal of this module is to provide base capabilities for creating and managing web contents.

Note that this module does not provide a whole theme,
but gives you the right tools to create yours.
So you should build your own theme to expose your content, navigation, etc.


Main features
-------------

* Separation of concerns between ``page`` (content) and ``view`` (presentation)

    A page is the content you publish and you can assign a view to it.
    A view is just an Odoo template that present your content.

* Page types

    We define 2 basic types: `Simple` and `News`. You can add more
    and list, present, search pages in different ways based on types.

* Reusable views

    Create your own views according to your website design and reuse them when needed.

* Publish media and categorize it

    A ``media`` could be everything: an image, a video, a link to an image or a video.
    You can categorize it rely on auto-categorization based on mimetypes.
    Preview images are loaded automatically but you can customize them.

* Automatic navigation and site hierarchy

    A page can contain other pages, acting like a folder. By nesting pages you create a hierarchy.
    This can be used to show global and contextual navigation without having to
    customize menu links every now and then.

* Meaningful URLs

    Pages' URLs are built using their hierarchy.
    For instance, if you have a section `cars` that contains a sub section `sport`
    that contains a page 'Porche' the final URL will be `/cms/cars/sport/porche`.

* Manage redirects within page backend

    You can force a page to redirect to another page or to an external link,
    and you can choose which kind of redirect status code to use (301, 302, etc)

* Protect your content

    On each page you can decide who can view it (edit permission yet to come).
    This happens at page level not view's, so that you can have different pages
    presented with same view but with different permissions.

* Full text search

    The extra module ``website_cms_search`` adds features for doing full text searches.


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/CMS/issues>`_.
In case of trouble, please check there if your issue has already been reported.


Credits
=======

Contributors
------------

Read the `contributors list`_

.. _contributors list: ./AUTHORS

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
