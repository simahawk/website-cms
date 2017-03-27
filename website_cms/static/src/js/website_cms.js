odoo.define('website_cms.website_cms', function (require) {
    'use strict';

    var ajax = require('web.ajax');
    var core = require('web.core');
    var website = require('website.website');

    var _t = core._t;

    var lastsearch;

    $('input[name="tag_ids"].js_select2').select2({
        tags: true,
        tokenSeparators: [",", " ", "_"],
        maximumInputLength: 35,
        minimumInputLength: 2,
        maximumSelectionSize: 5,
        lastsearch: [],
        createSearchChoice: function (term) {
            if ($(lastsearch).filter(function () { return this.text.localeCompare(term) === 0;}).length === 0) {
                if ($('input[name="tag_ids"].js_select2').data('can-create')){
                    // use `data-can-create` attribute to turn on/off tag creation
                    return {
                        id: "_" + $.trim(term),
                        text: $.trim(term) + ' *',
                        isNew: true,
                    }
                }
            }
        },
        formatResult: function(term) {
            if (term.isNew) {
                return '<span class="label label-primary">New</span> ' + _.escape(term.text);
            }
            else {
                return _.escape(term.text);
            }
        },
        ajax: {
            url: '/cms/get_tags',
            dataType: 'json',
            data: function(term) {
                return {
                    q: term,
                    l: 50
                };
            },
            results: function(data) {
                var ret = [];
                _.each(data, function(x) {
                    ret.push({ id: x.id, text: x.name, isNew: false });
                });
                lastsearch = ret;
                return { results: ret };
            }
        },
        // Take default tags from the input value
        initSelection: function (element, callback) {
            var data = [];
            _.each(element.data('init-value'), function(x) {
                data.push({ id: x.id, text: x.name, isNew: false });
            });
            element.val('');
            callback(data);
        },
    });

});
