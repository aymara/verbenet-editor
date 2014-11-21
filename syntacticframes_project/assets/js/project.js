/* Project specific Javascript goes here. */

var def_opts = {
    'empty_text': '∅',
    'style': 'inedit'
};

function linebreaks(value) {
    /* Converts new lines into <p> and <br />s.
     * Should be as close as possible to django.utils.html.linebreaks
     * (the goal is to avoid reloading the page)
     */
    var para_list;

    // normalize newlines: \n\r is accepted by all browsers
    value = value.replace(/\n(?!\r)/g, "\n\r");
    para_list = value.split(/(?:\n\r){2,}/);
    para_list = para_list.map(function(para) {
        return '<p>' + para.replace('\n\r', '<br />') + '</p>';
    });
    return para_list.join('\n\r\n\r')
}

function editable_class_fields() {
    // Edit all editable fields
    $('.frame_editable').each(function() {
        $(this).unbind();
        $(this).inedit($.extend({}, def_opts, {onEnd: edited_frame_field, empty_text: '∅'}));
    });

    $('.role_editable').each(function() {
        $(this).unbind();
        $(this).inedit($.extend({}, def_opts, {onEnd: edited_role_field}));
    });

    $('.frameset_editable').each(function() {
        var field = $(this).data('field');
        $(this).unbind();
        $('.frameset_editable .external').click(function(e) { e.stopPropagation(); });
        if (field === 'comment' || field == 'ladl_string' || field == 'lvf_string') {
            $(this).inedit($.extend({}, def_opts, {onStart: call_resize_textarea, onEnd: edited_frameset_field, type: 'textarea'}));
        } else {
            $(this).inedit($.extend({}, def_opts, {onEnd: edited_frameset_field}));
        }
    });

    $('.class_editable').each(function() {
        $(this).unbind();
        $(this).inedit($.extend({}, def_opts, {onStart: call_resize_textarea, onEnd: edited_class_field, type: 'textarea'}));
    });

    $('.levin_editable').each(function() {
        $(this).unbind();
        $(this).inedit($.extend({}, def_opts, {onStart: call_resize_textarea, onEnd: edited_levin_field, type: 'textarea'}));
    });
}

/* Replace edited class */
function update_class(here) {
    var vn_class_article = $(here).closest("article");
    var vn_class_id = vn_class_article.attr('id');

    request = $.ajax({url: '/vn_class/' + vn_class_id + '/'});
    request.done(function(response, textStatus, jqXHR) {
        $(vn_class_article).replaceWith(response);
        show_plus();
        editable_class_fields();
    });
}

// get a cookie using jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
function sameOrigin(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
}

function edited_frame_field(input_field, span) {
    var new_val = $(input_field).val();

    var vn_class_id = $(span).closest("article").attr('id');
    var frame_id = $(span).closest(".frame").data("frameid");

    var request = $.ajax({
        url: '/update/',
        type: 'POST',
        data: {
            type: 'frame',
            field: $(span).data("field"),
            vn_class: vn_class_id,
            frame_id: frame_id,
            label: new_val,
        }
    });
}

function edited_role_field(input_field, span) {
    var new_val = $(input_field).val();
    var vn_role_id = $(span).data('role_id');
    var frameset_id = $(span).closest(".subclass").attr('id');

    var request = $.ajax({
        url: '/update/',
        type: 'POST',
        data: {
            type: 'role',
            field: 'N/A',
            label: new_val,
            vn_role_id: vn_role_id,
            frameset_id: frameset_id
        }
    });
}

function edited_frameset_field(input_field, span) {
    var that = span;
    var new_val = $(input_field).val();

    var vn_class_id = $(span).closest("article").attr('id');
    var frameset_id = $(span).closest(".subclass").attr('id');
    var field = $(span).data("field");

    var request = $.ajax({
        url: '/update/',
        type: 'POST',
        data: {
            type: 'frameset',
            field: field,
            vn_class: vn_class_id,
            frameset_id: frameset_id,
            label: new_val,
        }
    });

    if ($(span).data('field') == 'comment') {
        if (new_val.trim() == '') {
            new_val = def_opts.empty_text
        }
        var formatted_new_val = linebreaks(new_val);
        $(span).html(formatted_new_val);
    } else {
        request.done(function() { update_class(that); });
    }
}

function edited_class_field(input_field, span) {
    var that = span;
    var new_val = $(input_field).val();
    var formatted_new_val = linebreaks(new_val);
    $(span).html(formatted_new_val);

    var vn_class_id = $(span).closest('article').attr('id')

    var request = $.ajax({
        url: '/update/',
        type: 'POST',
        data: {
            type: 'vn_class',
            field: 'comment',
            vn_class: vn_class_id,
            label: new_val,
        }
    });
}

function edited_levin_field(input_field, span) {
    var that = span;
    var new_val = $(input_field).val();
    var formatted_new_val = linebreaks(new_val);
    $(span).html(formatted_new_val);

    var request = $.ajax({
        url: '/update/',
        type: 'POST',
        data: {
            type: 'levin',
            field: 'comment',
            levin_number: $(that).data('levinnumber'),
            label: new_val,
        }
    });
}

function call_resize_textarea(textarea) {
    resize_textarea(textarea[0]);
}

function resize_textarea(textarea) {
    while($(textarea).outerHeight() < textarea.scrollHeight + parseFloat($(textarea).css("borderTopWidth")) + parseFloat($(textarea).css("borderBottomWidth"))) {
        $(textarea).height($(textarea).height()+1);
    };
}

$(document).ready(function() {
    // Not 'toggle' to keep synchronised
    $(document).on("mouseenter", ".role", function() { $(this).find('a').addClass('visible'); });
    $(document).on("mouseleave", ".role", function() { $(this).find('a').removeClass('visible'); });

    if (window._user_authenticated) {

        var csrftoken = getCookie('csrftoken');
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                    // Send the token to same-origin, relative URLs only.
                    // Send the token only if the method warrants CSRF protection
                    // Using the CSRFToken value acquired earlier
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });

        var previous_timeout = -1;

        $(document).ajaxStart(function(e, request, settings) {
            $("#ajax-ok").hide();
            $("#ajax-loading").show();
        });
        $(document).ajaxSuccess(function(e, request, settings) {
            var is_vn_class = settings.url.indexOf("/vn_class/") == 0;
            var is_update = settings.url.indexOf("update") >= 0;
            var is_remove = settings.url.indexOf("remove") >= 0 && settings.data.indexOf('LevinClass') == -1;
            var is_validate_verbs = settings.url.indexOf("/validate/") == 0 && settings.data.indexOf('VerbNetFrameSetVerb') >= 0;
            var is_toggle_verb_validity = settings.url.indexOf('/togglevalidity') == 0;
            var is_lvf_or_ladl = settings.data != undefined && (settings.data.indexOf("lvf_string") >= 0 || settings.data.indexOf("ladl_string") >= 0);
            var is_send = settings.url.indexOf("send") >= 0;

            if(is_vn_class || (is_update && !is_lvf_or_ladl) || is_remove || is_validate_verbs || is_toggle_verb_validity || is_send) {
                $("#ajax-loading").hide();
                $("#ajax-ok").show();
                clearTimeout(previous_timeout);
                previous_timeout = setTimeout(function() {
                    $("#ajax-ok").fadeOut('slow');
                }, 10000);
            }
        });
        $(document).ajaxError(function(e, request, settings) {
            if (request.status == 403) {
                alert(request.responseText);
            } else {
                alert("Erreur : modification non prise en compte. Je vais regarder ce qui se passe.");
            }
            location.reload(true);
        });

        editable_class_fields();

        // validate all verbs
        $(document).on('click', '.validate_verbs > button', function() {
            var that = $(this);
            var category = that.data('verb-category');

            var verbs = that.closest('.subclass').find('span.translation').filter('.' + category);
            verbs.removeClass('INFERRED').addClass('VALID');
            verbs.each(function() {
                if ($(this).parent().is("del")) {
                    $(this).unwrap();
                }
            });

            var request = $.ajax({
                url: '/validate/',
                type: 'POST',
                data: {
                    model: 'VerbNetFrameSetVerb',
                    frameset_name: that.data('frameset_id'),
                    category: category,
                }
            });

            return false;
        });

        // toggle verb validity
        $(document).on('click', 'span.translation', function() {
            var that = $(this);
            var new_status;

            if (that.hasClass('INFERRED')) {
                // validate
                that.removeClass('INFERRED').addClass('VALID');
                new_status = 'VALID';
            } else if (that.hasClass('VALID')) {
                // invalidate
                that.removeClass('VALID').addClass('WRONG').wrap('<del></del>');
                new_status = 'WRONG';
            } else if (that.hasClass('WRONG')) {
                // get back to inferred
                that.removeClass('WRONG').addClass('INFERRED').unwrap();
                new_status = 'INFERRED';
            } else {
                // notify bug
                new_status = 'IMPOSSIBLE';
            }

            // send new status
            var request = $.ajax({
                url: '/togglevalidity/',
                type: 'POST',
                data: {
                    verb_id: that.data('verb_id'),
                    new_status: new_status,
                }
            });

            return false;
        });

        // validate Levin class
        $(document).on('click', '.validate_class', function() {
            var that = $(this);

            var request = $.ajax({
                url: '/validate/',
                type: 'POST',
                data: {
                    model: 'LevinClass',
                    levin_class: that.data('levinid')
                }
            });

            request.done(function() { document.location.reload(true); });
            return false;
        });

        // remove Levin class
        $(document).on('click', '.remove_class', function() {
            var that = $(this);

            var request = $.ajax({
                url: '/remove/',
                type: 'POST',
                data: {
                    model: 'LevinClass',
                    levin_number: that.data('levinid')
                }
            });

            request.done(function() { document.location.reload(true); });
            return false;
        });

        // remove frame
        $(document).on('click', '.remove_frame', function() {
            var that = this;
            var vn_class_id = $(this).closest("article").attr('id');
            var frame_id = $(this).closest(".frame").data("frameid");

            var request = $.ajax({
                url: '/remove/',
                type: 'POST',
                data: {
                    model: 'VerbNetFrame',
                    vn_class: vn_class_id,
                    frame_id: frame_id,
                }
            });

            request.done(function() { update_class(that); });
            return false;
        });

        // new frame
        $(document).on('click', 'button.new_frame', function() {
            $(this).hide();
            var form = $(this).parent().next(".frame");
            form.slideDown();
        });

        $(document).on('submit', 'form.new_frame', function() {
            var that = this;
            var data = $(this).serialize();
            var request = $.post($(this).attr('action'), data);

            request.done(function() { update_class(that); });

            return false;
        });

        // send verbs to another frameset
        $(document).on('click', 'button.send_verbs_to', function() {
            $(this).parent().find('form').slideDown();
        });

        $(document).on('submit', '.send_verbs form', function() {
            var that = this;
            var data = $(this).serialize();
            var request = $.post($(this).attr('action'), data);

            request.done(function() { document.location.reload(true); });

            return false;
        });

        // new subclass
        $(document).on('click', '.new_subclass button', function() {
            var that = this;

            var request = $.ajax({
                url: '/add/',
                type: 'POST',
                data: {
                   type: 'subclass',
                   frameset_id: $(this).data("frameset_id"),
                }
            });

            request.done(function() { update_class(that); });
            return false;
        });

        // remove subclass
        $(document).on('click', 'button.remove_subclass', function() {
            var that = this;

            var request = $.ajax({
                url: '/remove/',
                type: 'POST',
                data: {
                    model: 'VerbNetFrameSet',
                    frameset_id: $(this).data("frameset_id"),
                }
            });

            request.done(function() { update_class(that); });
            return false;
        });

        // show subclass
        $(document).on('click', 'button.show_subclass', function() {
            var that = this;

            var request = $.ajax({
                url: '/show/',
                type: 'POST',
                data: {
                    model: 'VerbNetFrameSet',
                    frameset_id: $(this).data("frameset_id"),
                }
            });
            request.done(function() { update_class(that); });
            return false;
        });

        // show frame
        $(document).on('click', 'button.show_frame', function() {
            var that = this;

            var request = $.ajax({
                url: '/show/',
                type: 'POST',
                data: {
                    model: 'VerbNetFrame',
                    frame_id: $(this).data("frame_id")
                }
            });

            request.done(function() { update_class(that); });
            return false;
        });

        $(document).on('keyup', 'textarea', function(e) {
            resize_textarea(this);
        });

        // add translation
        function added_translation(input_field, span) {
            var that = span;
            var request = $.ajax({
                url: '/add/',
                type: 'POST',
                data: {
                    type: 'translation',
                    label: $(input_field).val(),
                    frameset_id: $(span).closest('.subclass').attr('id'),
                }
            });
            request.done(function() { update_class(that); });
        }

        $(document).on('click', '.new_translation_link', function() {
            var span = $(this).parent().find('.new_translation_editable');
            $(span).inedit($.extend({}, def_opts, {onEnd: added_translation, empty_text: ''}));
            $(span).trigger('click');
            return false;
        });

        // add role
        function added_role(input_field, span) {
            var that = span;
            var request = $.ajax({
                url: '/add/',
                type: 'POST',
                data: {
                    type: 'role',
                    label: $(input_field).val(),
                    frameset_id: $(span).closest('.subclass').attr('id'),
                }
            });
            request.done(function() { update_class(that); });
        }

        $(document).on('click', '.new_role', function() {
            var span = $(this).parent().find('.new_role_editable');
            $(span).inedit($.extend({}, def_opts, {onEnd: added_role, empty_text: ''}));
            $(span).trigger('click');
            return false;
        });

        // remove role
        $(document).on('click', '.remove_role', function() {
            var frameset_id = $(this).closest(".subclass").attr('id');
            var role_id = $(this).closest('.role').find('.role_editable').data('role_id')

            $(this).closest('.role').fadeOut();

            var request = $.ajax({
                url: '/remove/',
                type: 'POST',
                data: {
                    model: 'VerbNetRole',
                    frameset_id: frameset_id,
                    role_id: role_id,
                }
            });

            return false;
        });

    }
});

