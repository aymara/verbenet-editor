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

        var styleClassName  = "";
        var styleObject     = null;

        // parse a style argument
        if ((typeof options.style == 'string') && (jQuery.trim(options.style) != "")){
            styleClassName = 'class="' + options.style + '"';
        }

        if (typeof options.style == 'object') {
            styleObject = options.style;
        }

        // define input elements
        var inputElement = new Array();
        inputElement[0] = '<input    style="display:none" ' + styleClassName + ' value="" type="text" />';
        inputElement[1] = '<textarea style="display:none" ' + styleClassName + ' > </textarea>';

        options.clickStarted = false;

        // for each selected field do this
        jQuery(selection).each(function(){
            var selected = this;

            // on click function
            jQuery(selected).bind(event.click, function(){
                var text;
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

                var input = null;

                // remove text from text label
                jQuery(selected).text("");

                // append input element after selected dom element
                switch (options.position){
                    case 'after':
                        jQuery(selected).after(inputElement[indexType]);
                        input = jQuery(selected).next();
                        break;
                    case 'before':
                        jQuery(selected).before(inputElement[indexType]);
                        input = jQuery(selected).prev();
                        break;
                    case 'in':
                        jQuery(selected).append(inputElement[indexType]);
                        input = jQuery(selected).find(options.type);
                        break;
                }

                // save data on Enter
                jQuery(input).bind(event.keypress, function(e) {
                    var code = (e.keyCode ? e.keyCode : e.which);
                    if(code == 13) {
                        // enable on click event
                        options.clickStarted = false;

                        // execute on blur method
                        var result = options.onEnd(input, selected);
                        if((typeof result === 'undefined') || (result == true)) {

                            // update label and remove the input field
                            var newText = jQuery(input).val();
                            jQuery(selected).data("text", newText);
                            jQuery(selected).text(newText);
                            jQuery(selected).show();
                            jQuery(input).remove();
                        }
                    }
                });

                // @ focus call onStart functions
                jQuery(input).bind(event.focus, function() {
                    // execute on focus method
                    options.onStart(input, selected);
                });

                // assign style from given object to input field
                if (styleObject != null){
                    for (s in styleObject){
                        jQuery(input).css(s, styleObject[s]);
                    }
                }

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
