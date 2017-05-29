.. image:: https://img.shields.io/badge/licence-lgpl--3-blue.png
   :target: http://www.gnu.org/licenses/LGPL-3.0-standalone.html
   :alt: License: LGPL-3

=========
CMS mixin
=========

Base behaviors for CMS contents.

Provided mixins:

* ``cms.orderable.mixin``
* ``cms.coremetadata.mixin``
* ``cms.content.mixin``


Orderable mixin
---------------

Implements basic ordering features:

* order model by `sequence desc` by default
* last created item has always higher sequence

Usage:

.. code:: python

    class OrderableModel(models.Model):
        _name = 'my.orderable'
        _inherit = [
            'website.published.mixin',
            'cms.orderable.mixin',
        ]


Coremetadata mixin
------------------

Implements basic core metadata features:

* exposes create/write fields:

    `create_uid`, `write_uid`, `create_date`, `write_date`

  so that you can use them directly in views and forms

* adds new fields:

    * `publish_uid` to track who published an item
    * `publish_date` to track when an item has been published

Usage:

.. code:: python

    class CoremetadataModel(models.Model):
        _name = 'my.coremetadata'
        _inherit = [
            'website.published.mixin',
            'cms.coremetadata.mixin',
        ]


Content mixin
-------------

Implements basic website content features:

* uses following mixins by default:

    * ``website.published.mixin``
    * ``cms.coremetadata.mixin``
    * ``cms.orderable.mixin``

* adds basic fields:

    * `name`
    * `description` brief description of the content
    * `body` to contain HTML content

Usage:

.. code:: python

    class ContentModel(models.Model):
        _name = 'my.content'
        _inherit = [
            'cms.content.mixin',
        ]


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/website-cms/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.


Credits
=======

Images
------

* Odoo Community Association: `Icon <https://odoo-community.org/logo.png>`_.

Contributors
------------

* Simone Orsi <simone.orsi@camptocamp.com

Do not contact contributors directly about support or help with technical issues.


Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
