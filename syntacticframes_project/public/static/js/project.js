/* Project specific Javascript goes here. */

function show_plus() {
    // Show/hide verbs that are not interesting
    var showLink = $('<a/>').attr('class', 'plus_link').text('[+]').prop('href', '#');
    $(document).on("click", ".plus_link", toggleHideShow);
    $('.translations a').remove();
    $('.translations').each(function() {
        if ($(this).find('span').size() > 0) {
            $(this).append(showLink.clone());
        }
    });
}

function editable_class_fields() {
    // Edit all editable fields
    $('.frame_editable').each(function() {
        $(this).inedit({'onEnd': edited_frame_field});
    });

    $('.frameset_editable').each(function() {
        $(this).inedit({'onEnd': edited_frameset_field});
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

/* Highlight translations */
function toggleHighlightMembers() {
    var origins = $(this).data('origin').split(',');
    $('.members span').each(function() {
        if (origins.indexOf($(this).text()) != -1) {
            $(this).toggleClass('hover');
        }
    });
}

/* Highlight origins */
function toggleHighlightCandidates() {
    var origin = $(this).text();
    $(this).parent().parent().find('.translations span').each(function() {
        if ($(this).data('origin').split(',').indexOf(origin) != -1) {
            $(this).toggleClass('hover');
        }
    });
}

/* Hide dark/gray translations */
function toggleHideShow(e) {
    e.preventDefault();
    $(this).parent().find('span.unknown').toggle();
    $(this).parent().find('span.dicovalence').toggle();
    $(this).text($(this).text() == '[+]' ? '[-]' : '[+]');
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
            field: $(span).data("field"),
            vn_class: vn_class_id,
            frame_id: frame_id,
            label: new_val,
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
            field: field,
            vn_class: vn_class_id,
            frameset_id: frameset_id,
            label: new_val,
        }
    });


    if (field == 'lvf_string' || field == 'ladl_string') {
        request.done(function() { update_class(that); });
    }
}

$(document).ready(function() {
    // Show relation between verbs and origin
    $('.translations span').hover(toggleHighlightMembers, toggleHighlightMembers);
    $('.members span').hover(toggleHighlightCandidates, toggleHighlightCandidates);

    // Show dark/gray verbs
    show_plus();

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
        var is_lvf_or_ladl = settings.data != undefined && (settings.data.indexOf("lvf_string") >= 0 || settings.data.indexOf("ladl_string") >= 0);
        if(is_vn_class || (is_update && !is_lvf_or_ladl)) {
            $("#ajax-loading").hide();
            $("#ajax-ok").show();
            clearTimeout(previous_timeout);
            previous_timeout = setTimeout(function() {
                $("#ajax-ok").fadeOut('slow');
            }, 10000);
        }
    });
    $(document).ajaxError(function(e, request, settings) {
        alert("Erreur : modification non prise en compte. Je vais regarder ce qui se passe.");
        location.reload(true);
    });

    editable_class_fields();

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

    // new subclass
    $(document).on('click', 'button.new_subclass', function() {
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
              

});

