/* Copyright 2016 OCA/oscar@vauxoo.com
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */
odoo.define("website_cms.tour", function (require) {
    "use strict";

    var Tour = require("web.Tour");

    Tour.register({
        id: "test_create_page",
        name: "Try to create a page and view it",
        path: "/cms/add-page",
        mode: "test",
        steps: [
            {
                title: "Fill form with the data to create the 'Demo Page'",
                element: "button.btn-primary:contains(Submit)",
                onload: function () {
                    $('input[name="name"]').val('Demo Page');
                    $('input[name="description"]').val('Demo Page Description');

                },
            },
            {
                title: "Wait for the page editor to be displayed",
                waitFor: "div:contains(Insert Blocks)",

            },
        ]
    });

});
