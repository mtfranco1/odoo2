odoo.define('delivery_schedule_view.DeliverScheduleView', function(require){
    "use_strict";

    var AbstractController = require('web.AbstractController');
    var AbstractModel = require('web.AbstractModel');
    var AbstractRenderer = require('web.AbstractRenderer');
    var AbstractView = require('web.AbstractView');
    var viewRegistry = require('web.view_registry');

    var DSController = AbstractController.extend({});
    var DSRenderer = AbstractRenderer.extend({
        className: "class(es) to put on element",
        _render: function () {
            // this.$el
            // render stuff on the view
            return $.when();
        },
        on_attach_callback: function (){
            // do stuff when view is attached.
            // Late Start
        },
    });
    var DSModel = AbstractModel.extend({
        reload: function(id,params){
            return this.load(params);
        },
        // access arch(root element <form> or whatever) attributes with params.whatever_attribute;
    });

    var DSView = AbstractView.extend({
        config: {
            Model: DSModel,
            Controller: DSController,
            Renderer: DSRenderer,
        },
        viewType = 'delivery_schedule',
        // access arch(root element <form> or whatever) attributes with this.arch.attrs.whatever;
    });

    viewRegistry.add('delivery_schedule',DSView);

    return DSView;
})
