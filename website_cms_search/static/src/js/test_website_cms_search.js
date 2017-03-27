/* Copyright 2016 OCA/oscar@vauxoo.com
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */
odoo.define('website_sale.test', function (require) {
'use strict';

var core = require('web.core');
var Tour = require('web.Tour');

var _t = core._t;

var steps = Tour.tours.test_create_page.steps;
for (var k=0; k<steps.length; k++) {
    if (steps[k].title === "Wait for the page editor to be displayed") {
        steps.splice(k+1, 0,             {
                title: "Click on Search Button",
                waitFor: "a:contains(Search Page)",
                element: "a:contains(Search Page)",
            },
            {
                title: "Search for the recently created page 'Demo Page'",
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
            });
        break;
    }
}
});
