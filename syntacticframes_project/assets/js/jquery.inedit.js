/*
 * jQuery inedit version 1.04
 *
 * Date: 15/09/2012
 * Author: Zeamy Team
 * Contact: contact@zeamy.com
 * Website: http://www.webolitic.com/inedit
 *
 * Copyright (c) 2012 webolitic.com
 * http://www.opensource.org/licenses/mit-license.php
 *
 * Date: 26/03/2014
 * Updates by Quentin Pradet
 */

(function(jQuery){

    // selectors
    var event = {
        click: 'click',
        blur: 'blur',
        focus: 'focus',
        keypress: 'keypress'
    };

    // inedit function
    jQuery.fn.inedit = function(opts){

        // variables
        var selection  = this;
        var types      = ['input', 'textarea'];
        var positions  = ['before', 'after', 'in'];
        var options    = jQuery.extend({},jQuery.fn.inedit.options, opts);
        var indexType  = jQuery.inArray(options.type, types);
        var indexPos   = jQuery.inArray(options.position, positions);
        var inputElement;


        // check if type is correct
        if (indexType < 0){
            console.log('Unknown type "' + options.type + '"');
            return this;
        }

        // check if position is correct
        if (indexPos < 0){
            console.log('Unknown type "' + options.position + '"');
            return this;
        }

        // define input elements
        inputElement = [
            jQuery('<input />', {'class': options.style, 'type': 'text'}),
            jQuery('<textarea />', {'class': options.style }),
        ]

        options.clickStarted = false;

        // for each selected field do this
        jQuery(selection).each(function(){
            var selected = this;


            // on click function
            jQuery(selected).bind(event.click, function(){

                var text;
                var input = null;
                var validate_button;
                var data_text = jQuery(selected).data('text');

                // prevent to start handler multiple times
                if (options.clickStarted == true) return;

                options.clickStarted = true;

                // fetch the text to edit
                if (data_text) {
                    text = data_text;
                } else {
                    text = jQuery(selected).text();
                }

                // if text contains empty_text, start with empty string
                if (options.empty_text == text) {
                    text = '';
                }

                // remove text from text label
                jQuery(selected).text("");

                // append input element after selected dom element
                switch (options.position){
                    case 'after':
                        jQuery(selected).after(inputElement[indexType].clone());
                        input = jQuery(selected).next();
                        break;
                    case 'before':
                        jQuery(selected).before(inputElement[indexType].clone());
                        input = jQuery(selected).prev();
                        break;
                    case 'in':
                        jQuery(selected).append(inputElement[indexType].clone());
                        input = jQuery(selected).find(options.type);
                        break;
                }

                validate_button = jQuery('<button>', {
                    'type': 'submit',
                    'value': 'Confirmer',
                    'class': 'btn btn-primary ' + options.style}).text('Confirmer');
                jQuery(input).after(validate_button);

                // save data on Enter
                jQuery(validate_button).bind(event.click, function(e) {
                    // enable on click event
                    options.clickStarted = false;

                    // update label and remove the input field
                    var newText = jQuery(input).val();
                    jQuery(selected).data("text", newText);
                    jQuery(selected).text(newText);
                    jQuery(selected).show();
                    jQuery(input).remove();
                    jQuery(validate_button).remove();

                    // execute user method
                    var result = options.onEnd(input, selected);
                });

                // @ focus call onStart functions
                jQuery(input).bind(event.focus, function() {
                    // execute on focus method
                    options.onStart(input, selected);
                });

                jQuery(input).val(text);
                jQuery(input).show();
                jQuery(input).focus();
            });
        });

        return this;
    }

    // inedit options
    jQuery.fn.inedit.options = {
        type: 'input',
        onStart: jQuery.noop,
        onEnd: jQuery.noop,
        style: "",
        position: 'after',
        empty_text: '',
    };

})(jQuery);
