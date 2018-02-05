odoo.define('cms_form.master_slave', function (require) {
    'use strict';
    /*
    Handle master / slave fields automatically.
    TODO: explain behavior.
    */

    // TODO: this does not work ATM as it's loaded only in backend assets
    // and requires backend dependencies :(
    // var pyeval = require('web.pyeval');
    var sAnimation = require('website.content.snippets.animation');

    sAnimation.registry.CMSFormMasterSlave = sAnimation.Class.extend({
      selector: ".cms_form_wrapper form",
      start: function (editable_mode) {
        this.data = this.$el.data('form');
        this.setup_handlers();
        this.load_master_slave();
      },
      setup_handlers: function(){
        this.handlers = {
          'hide': $.proxy(this.handle_hide, this),
          'show': $.proxy(this.handle_show, this),
          'readonly': $.proxy(this.handle_readonly, this),
          'no_readonly': $.proxy(this.handle_no_readonly, this),
          'required': $.proxy(this.handle_required, this),
          'no_required': $.proxy(this.handle_no_required, this),
          'domain': $.proxy(this.handle_domain, this),
          'no_domain': $.proxy(this.handle_no_domain, this)
        };
      },
      load_master_slave: function(){
        var self = this;
        $.each(this.data.master_slave, function(master, slaves){
          var $master_input = $('[name="' + master +'"]');
          $.each(slaves, function(action, mapping){
            var handler = self.handlers[action];
            if (handler) {
              $master_input.on('change', function(){
                var $input = $(this),
                    master_val = $input.val();
                if ($input.is(':checkbox')) {
                  // value == 'on' => true/false
                  master_val = $input.is(':checked');
                }
                $.each(mapping, function(slave_fname, condition){
                  if (action == 'domain') {
                    handler(slave_fname, master_val, condition);
                  }
                  else if (_.contains(condition, master_val)) {
                    handler(slave_fname, master_val);
                  }
                });
              }).filter('select,[type=checkbox],[type=text]').trigger('change'); // trigger change only for specific inputs
            }
          })
        })
      },
      handle_hide: function(slave_fname, master_val){
        $('[name="' + slave_fname +'"]').closest('.form-group').hide();
      },
      handle_show: function(slave_fname, master_val){
        $('[name="' + slave_fname +'"]').closest('.form-group').show();
      },
      handle_readonly: function(slave_fname, master_val){
        $('[name="' + slave_fname +'"]')
          .attr('disabled', 'disabled')
          .closest('.form-group').addClass('disabled');
      },
      handle_no_readonly: function(slave_fname, master_val){
        $('[name="' + slave_fname +'"]')
          .attr('disabled', null)
          .closest('.form-group').removeClass('disabled');
      },
      handle_required: function(slave_fname, master_val){
        $('[name="' + slave_fname +'"]').attr('required', 'required');
      },
      handle_no_required: function(slave_fname, master_val){
        $('[name="' + slave_fname +'"]').attr('required', null);
      },
      handle_domain: function(slave_fname, master_val, condition){
        var domain = [];
        master_val = parseInt(master_val);
        if (!master_val) {
          this.handle_no_domain(slave_fname, master_val, condition);
        } else {
          // TODO: check w/ some JS guru how to improve this and make it safe
          eval("domain = " + condition + ";")
          $('[name="' + slave_fname +'"]').data('domain', domain);
        }
      },
      handle_no_domain: function(slave_fname, master_val, condition){
        $('[name="' + slave_fname +'"]').data('domain', []);
      }
    });

});
