[![Runbot Status](https://runbot.odoo-community.org/runbot/badge/flat/225/9.0.svg)](https://runbot.odoo-community.org/runbot/repo/github-com-oca-website-cms-225)
[![Build Status](https://travis-ci.org/OCA/website-cms.svg?branch=9.0)](https://travis-ci.org/OCA/website-cms)
[![Coverage Status](https://coveralls.io/repos/OCA/website-cms/badge.svg?branch=9.0&service=github)](https://coveralls.io/github/OCA/website-cms?branch=9.0)

CMS Features for Odoo Website
=============================

Includes modules that add advanced CMS functionalities to Odoo.

Main features
-------------

* Separation of concerns between ``page`` (content) and ``view`` (presentation)
* Page types (simple, news, you-own-type)
* Reusable views (create a CMS view and reuse it on your CMS pages)
* Publish media and categorize it
* Automatic navigation and site hierarchy
* Meaningful URLs (read: "speaking URLs")
* Manage redirects within page backend
* Protect your content (set permissions on each page rather than view)
* Full text search

Roadmap
-------

* Improve frontend forms (manage media, reuse backend forms)
* Independent translations branches (skip odoo translation mechanism on demand via configuration)
* Edit permissions control / sharing facilities / notifications, etc
* Simplified interface for managing users and groups
* Publication workflow management
* Content history / versioning
* Full text search using PG built-in search engine (see fts modules)
* Shorter URLs (drop path ids for instance)
* Performance fixes/tuning (use parent_left/right for instance)
* Introduce portlets for sidebar elements
* Add "collections" to fetch contents from the whole website (eg: "News from 2016")
* Improve test coverage
* Default theme


[//]: # (addons)
This part will be replaced when running the oca-gen-addons-table script from OCA/maintainer-tools.
[//]: # (end addons)

Translation Status
------------------
[![Transifex Status](https://www.transifex.com/projects/p/OCA-website-cms-9-0/chart/image_png)](https://www.transifex.com/projects/p/${ORG_NAME}-website-cms-website-cms)

----

OCA, or the [Odoo Community Association](http://odoo-community.org/), is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.
