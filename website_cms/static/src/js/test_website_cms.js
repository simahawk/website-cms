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
                    $('textarea[name="description"]').val('Demo Page Description');
                    $('input.select2-input.select2-default').val('TestTag');
                },
            },
            {
                title: "Wait for the page editor to be displayed",
                waitFor: "div:contains(Insert Blocks)",
                element: "a:contains(Search Page)",
            },
            {
                tile: "Search for the recently created page 'Demo Page'",
                waitFor: "input[name='search_text']",
                onload: function() {
                    $("input[name='search_text']").val('page');
                },
                element: "button:contains(Go!)",
            },
            {
                title: "Verify that the search results returned the page created",
                waitFor: "a.name:contains(Demo Page)",
                element: "a.name:contains(Demo Page)",
            },
            {
                title: "Click on 'Metadata' link in order to edit the page created",
                waitFor: "li.edit.edit-frontend.ml16:contains(Metadata)",
                element: "a:contains(Metadata)",
            },
            {
                title: "Edit the page",
                waitFor: "h2:contains(Edit page)",
                element: "button.btn-primary:contains(Submit)",
                onload: function () {
                    $('input[name="name"]').val('Demo Page edited');
                    $('textarea[name="description"]').val('Demo Page Description Edited');
                    $('input.select2-input.select2-default').val('TestTagEdited');
                },
            },
            {
                title: "Wait for the success message of page edition",
                waitFor: "div.alert.alert-info.alert-dismissible:contains(Page updated.)",
            },

        ]
    });

});
