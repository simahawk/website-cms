.. image:: https://img.shields.io/badge/licence-lgpl--3-blue.svg
   :target: http://www.gnu.org/licenses/LGPL-3.0-standalone.html
   :alt: License: LGPL-3

================
CMS account form
================

Replace portal user's account form
with a specific `CMS form <https://github.com/OCA/website-cms/cms_form`_.

Features
--------

* full control on fields and their validation
* full control on form behavior
* full test coverage

Additionally:

* validate email
* if email is changed:
   * update user's login (yes, Odoo does that w/out notifying the user!)
   * force logout
   * for reset email password to validate new email

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/website-cms/issues>`_. In
case of trouble, please check there if your issue has already been
reported. If you spotted it first, help us smashing it by providing a
detailed and welcomed feedback.

Credits
=======

Contributors
------------

-  Simone Orsi - Camptocamp SA simone.orsi@camptocamp.com


Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization
whose mission is to support the collaborative development of Odoo
features and promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
