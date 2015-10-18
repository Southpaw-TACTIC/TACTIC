/*
---
name: MooDialog.Alert
description: Creates an Alert dialog
authors: Arian Stolwijk
license:  MIT-style license
requires: MooDialog
provides: MooDialog.Alert
...
*/


MooDialog.Alert = new Class({

	Extends: MooDialog,

	options: {
		okText: 'OK',
		focus: true,
		textPClass: 'MooDialogAlert',
        type: 'text'
	},

	initialize: function(msg, options){
		this.parent(options);

		var okButton = new Element('input[type=button]', {
			events: {
				click: this.close.bind(this)
                                    
			},
			value: this.options.okText
		});

                

                if (this.options.type == 'html') {
                    var html_p =  new Element('p.' + this.options.textPClass);
                    spt.behavior.replace_inner_html( html_p, msg );
                    this.setContent(
                            html_p,
                            new Element('div.buttons').adopt(okButton)
                    );
                }
                else {
                    this.setContent(
                            new Element('p.' + this.options.textPClass, {text: msg}),
                            new Element('div.buttons').adopt(okButton)
                    );
                }

		if (this.options.autoOpen) this.open();

		if (this.options.focus) this.addEvent('show', function(){
			okButton.focus()
		});

                /* tactic */
                if (this.options.click) {
                    okButton.addEvent('click', this.options.click);
                }

	},
       

});


/*
---
name: MooDialog.Confirm
description: Creates an Confirm Dialog
authors: Arian Stolwijk
license:  MIT-style license
requires: MooDialog
provides: [MooDialog.Confirm, Element.confirmLinkClick, Element.confirmFormSubmit]
...
*/


MooDialog.Confirm = new Class({

	Extends: MooDialog,

	options: {
		okText: 'OK',
		cancelText: 'Cancel',
		focus: true,
		textPClass: 'MooDialogConfirm',
                type: 'html'
	},

	initialize: function(msg, fn, fn1, options){
		this.parent(options);
		var emptyFn = function(){},
			self = this;

                //tactic: options to pass in args to fn and fn1
		this.fn_args = options.ok_args ? options.ok_args : [];
                this.fn1_args = options.cancel_args ? options.cancel_args : [];

		var buttons = [
			{fn: fn || emptyFn, txt: this.options.okText, args: this.fn_args},
			{fn: fn1 || emptyFn, txt: this.options.cancelText, args: this.fn1_args}
		].map(function(button){
			return new Element('input[type=button]', {
				events: {
					click: function(){
                                                //tactic: pass in fn args
                                                button.args ? button.fn(button.args) : button.fn();
						self.close();
					}
				},
				value: button.txt
			});
		});

                if (this.options.type == 'html') {
                    var html_p =  new Element('p.' + this.options.textPClass);
                    spt.behavior.replace_inner_html( html_p, msg );
                    this.setContent(
                            html_p,
                            new Element('div.buttons').adopt(buttons)
                    );
                    
                }
                else {
                    this.setContent(
                            new Element('p.' + this.options.textPClass, {text: msg}),
                            new Element('div.buttons').adopt(buttons)
                    );
                }
		if (this.options.autoOpen) this.open();

		if(this.options.focus) this.addEvent('show', function(){
			buttons[1].focus();
		});

	}
});


Element.implement({

	confirmLinkClick: function(msg, options){
		this.addEvent('click', function(e){
			e.stop();
			new MooDialog.Confirm(msg, function(){
				location.href = this.get('href');
			}.bind(this), null, options)
		});
		return this;
	},

	confirmFormSubmit: function(msg, options){
		this.addEvent('submit', function(e){
			e.stop();
			new MooDialog.Confirm(msg, function(){
				this.submit();
			}.bind(this), null, options)
		}.bind(this));
		return this;
	}

});

/*
---
name: MooDialog.Error
description: Creates an Error dialog
authors: Arian Stolwijk
license:  MIT-style license
requires: MooDialog
provides: MooDialog.Error
...
*/


MooDialog.Error = new Class({

	Extends: MooDialog.Alert,

	options: {
		textPClass: 'MooDialogError'
	},
        onInitialize: function(wrapper){
			wrapper.setStyle('opacity', 0);
			this.fx = new Fx.Morph(wrapper, {
				duration: 500,
				transition: Fx.Transitions.Elastic.easeOut
			});
			this.overlay = new Overlay(this.options.inject, {
				duration: this.options.duration
			});
			if (this.options.closeOnOverlayClick) this.overlay.addEvent('click', this.close.bind(this));
	},
	onBeforeOpen: function(){
			this.overlay.open();
			this.fx.start({
				'margin-left': [-100, -50],
				opacity: [0, 1]
			}).chain(function(){
				this.fireEvent('show');
			}.bind(this));
		},
        
        

});

/*
---
name: MooDialog.Fx
description: Overwrite the default events so the Dialogs are using Fx on open and close
authors: Arian Stolwijk
license: MIT-style license
requires: [Cores/Fx.Tween, Overlay]
provides: MooDialog.Fx
...
*/


MooDialog.implement('options', {

	duration: 100,
	closeOnOverlayClick: true,

	onInitialize: function(wrapper){
		/*tactic: with error, it slides in */

                this.fx = new Fx.Tween(wrapper, {
			property: 'opacity',
			duration: this.options.duration
		    }).set(0);

                /* tactic */
		this.overlay = new mooOverlay(this.options.inject, {
			duration: 200
		});
		if (this.options.closeOnOverlayClick) this.overlay.addEvent('click', this.close.bind(this));
	},

	onBeforeOpen: function(wrapper){
                this.overlay.open();
                //var width = this.overlay.container.getScrollSize().x;
                // var dialog_width = wrapper.getSize().x;
                    
                this.fx.start(1).chain(function(){
			this.fireEvent('show');
		}.bind(this));
	},

	onBeforeClose: function(wrapper){
               
                this.fx.start(0).chain(function(){
			this.fireEvent('hide');
		}.bind(this));
        /* tactic */
        var num = this.options.inject.getElements('.MooDialog');
        if (num.length <= 1)
		    this.overlay.close();

	}


});


//MooPrompt
//

MooDialog.Prompt = new Class({

	Extends: MooDialog,

	options: {
		okText: 'OK',
		focus: true,
		textPClass: 'MooDialogPrompt',
                textarea_default: '',
                textarea_width: '400px',
                textarea_height: '100px',
                custom_html : null

	},

	initialize: function(msg, fn, options){
		this.parent(options);
		if (!fn) fn = function(){};
                //tactic
                if (options.custom_html ) {
                    this.content.empty();
                    spt.behavior.replace_inner_html( this.content, options.custom_html );
                    //this.content.set('html', options.custom_widget);
                    this.content.adopt(options.custom_widget);


                    submitButton = new Element('input[type=submit].prompt_ok', {value: this.options.okText}),
                    submitButton.setStyles({'vertical-align':'bottom', 'padding': '4px', 'margin-left': '6px'});
                    formEvents = {
                                    submit: function(e){
                                            e.stop();
                                            this.show_progress();
                                            
                                            fn(submitButton);
                                            this.close();
                                    }.bind(this)
                            };   
                    var br = new Element('br');
                    var div = new Element('div').setStyles({'float':'right', 'margin': '4px'});
                    
                    div.adopt(submitButton);

                    var form = new Element('form.buttons', {events: formEvents}).adopt(br, div);
                    this.content.adopt(form);

                }
                else {
                     var textInput = new Element('textarea.textInput', {type: 'text', value: this.options.text_input_default}),
                            formEvents = {
                                    submit: function(e){
                                            e.stop();
                                            this.show_progress();
                                            fn(textInput.get('value'));
                                            this.close();
                                    }.bind(this)
                            };
                    textInput.setStyles({"width": this.options.textarea_width, "height": this.options.textarea_height,
                        "background": "#fff", "color": "#000"});
                    submitButton = new Element('input[type=submit].prompt_ok', {value: this.options.okText}),
                    submitButton.setStyles({'vertical-align':'bottom', 'padding': '4px', 'margin-left': '6px'});
                    
                    var br = new Element('br');
                    var div = new Element('div').setStyles({'float':'right', 'margin': '4px'});
                    
                    div.adopt(submitButton);
                    var form = new Element('form.buttons', {events: formEvents}).adopt(textInput, br, div);
                    
                    this.setContent(
                            new Element('p.' + this.options.textPClass, {text: msg}),
                            form
                            
                    );
                    if (this.options.focus) this.addEvent('show', function(){
			textInput.focus();
		    });
                }

		if (this.options.autoOpen) this.open();

	
	}
});
