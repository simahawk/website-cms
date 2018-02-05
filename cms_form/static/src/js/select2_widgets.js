odoo.define('cms_form.select2', function (require) {
  'use strict';
  /*
  Handle master / slave fields automatically.
  TODO: explain behavior.
  */

  // TODO: this does not work ATM :(
  // var pyeval = require('web.pyeval');

  var ajax = require('web.ajax');
  var weContext = require("web_editor.context");
  var sAnimation = require('website.content.snippets.animation');

  var CMSFormSelect2 = sAnimation.Class.extend({
    start: function (editable_mode) {
      this.setup_options();
      this.setup_widget();
      this.current_results = [];
    },
    setup_options: function(){
      this.w_options = {
        'query': $.proxy(this.s2_query, this),
        'initSelection': $.proxy(this.s2_initSelection, this),
      };
    },
    setup_widget: function(){
      this.$el.select2(this.w_options);
    },
    get_domain: function (options) {
      var self = this,
          domain = [];
      if (options.term){
        domain.push([
          self.$el.data('search_field') || 'name', 'ilike', '%' + options.term + '%'
        ])
      }
      // TODO: use data.CompundDomain to build domain
      // ATM it's just in backend assets
      // and requires both data.js and pyeval.js
      self.domain = _.union(domain, self.$el.data('domain'));
    },
    s2_query: function(options) {
      var self = this,
          domain = self.get_domain(options);
      ajax.jsonRpc("/web/dataset/call_kw", 'call', {
        model: self.$el.data('model'),
        method: 'search_read',
        args: [self.domain],
        kwargs: {
          fields: self.$el.data('fields'),
          context: weContext.get()
        }
      }).then($.proxy(self.s2_handle_query_results, self, options));
    },
    s2_handle_query_results: function (options, results) {
      var self = this;
      var display_name = self.$el.data('display_name');
      results.sort(function(a, b) {
        return a[display_name].localeCompare(b[display_name]);
      });
      var res = {
        results: []
      };
      _.each(results, function(x) {
        res.results.push({
          id: x.id,
          text: x[display_name],
          isNew: false
        });
      });
      self.current_results = res.results;
      options.callback(res);
    },
    s2_initSelection: function(element, callback) {
      var value = element.data('init-value');
      element.val(value.id);
      callback(value);
    }
  });

  sAnimation.registry.CMSFormSelect2M2O = CMSFormSelect2.extend({
    selector: ".js_select2_x2x_widget.m2o",
    setup_options: function(){
      this._super()
      this.w_options = _.extend(this.w_options, {
        'multiple': false
      });
    }
  });

  sAnimation.registry.CMSFormSelect2X2M = CMSFormSelect2.extend({
    selector: ".js_select2_x2x_widget.x2m",
    setup_options: function(){
      this._super()
      this.w_options = _.extend(this.w_options, {
        'multiple': true,
        'tags': true,
        'tokenSeparators': [",", " ", "_"],
        'formatResult': $.proxy(this.s2_formatResult, this),
      });
    },
    s2_formatResult: function(term) {
      if (term.isNew) {
        return '<span class="label label-primary">New</span> ' + _.escape(term.text);
      } else {
        return _.escape(term.text);
      }
    }
  });

});
