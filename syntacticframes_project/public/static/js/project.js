/* Project specific Javascript goes here. */

/* Validating/refusing translations */
/*
function getColorId(color) {
    if (color == 'both') { return 0; }
    else if (color == 'ladl') { return 1; }
    else if (color == 'lvf') { return 2; }
    else if (color == 'dicovalence') { return 3; }
    else { return 4; }
}

function sortUL(list) {
    list.children(".comma_hack").remove();
    list.children("li").sort(function(a, b) {
        var idA = getColorId($(a).attr('class'));
        var idB = getColorId($(b).attr('class'));

        var upA = $(a).text();
        var upB = $(b).text();
        var cmpText = (upA < upB) ? -1 : (upA > upB) ? 1 : 0;
        return (idA < idB) ? -1 : (idA > idB) ? 1 : cmpText;
    }).appendTo(list);
    span = $('<span />').addClass('comma_hack').text(', ');
    list.find('li').after(span);
}
*/

/* Highlight translations */
function toggleHighlightMembers() {
    var origins = $(this).data('origin').split(',');
    $('.verbnet_members li').each(function() {
        if (origins.indexOf($(this).text()) != -1) {
            $(this).toggleClass('hover');
        }
    });
}

/* Highlight origins */
function toggleHighlightCandidates() {
    var origin = $(this).text();
    $(this).parent().parent().find('.evaluate li').each(function() {
        if ($(this).data('origin').split(',').indexOf(origin) != -1) {
            $(this).toggleClass('hover');
        }
    });
}

/* Hide dark/gray translations */
function toggleHideShow(e) {
    e.preventDefault();
    $(this).parent().find('li[class="unknown"]').toggle();
    $(this).parent().find('li[class="dicovalence"]').toggle();
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

/* Send change to server after edited in place */
function edited_class_field(input_field, span) {
    var new_val = $(input_field).val();
    var vn_class = $(span).parent().attr("id");

    $.ajax({
        url: '/update/',
        type: 'POST',
        data: {vn_class: vn_class, field: $(span).data("field"), label: new_val}
    });
}

function edited_frame_field(input_field, span) {
    var new_val = $(input_field).val();

    var vn_class_article = $(span).closest("article")[0];
    var vn_class_id = $(vn_class_article).find("h2").attr("id");

    var frame_div = $(span).closest(".frame")[0];
    var frame_id = $(frame_div).data("frameid");

    $.ajax({
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


$(document).ready(function() {
    // "Evaluate" a word: set it as valid or not
    /*
    $('.evaluate li').click(function() {
        // Retrieve the word, its status, and the other list
        var word = $(this);
        var wanted = word.parent().hasClass('valid') ? 'invalid': 'valid';
        var other_list = $(this).parent().parent().find('.'+wanted);

        // Move the word to the other list and append a space
        word.hide()
        sortUL(word.parent());

        other_list.append(word);
        span = $('<span />').addClass('comma_hack').text(', ');
        other_list.append(span);
        sortUL(other_list);

        word.fadeIn('slow');
    });
    */

    // Show relation between verbs and origin
    $('.evaluate li').hover(toggleHighlightMembers, toggleHighlightMembers);
    $('.verbnet_members li').hover(toggleHighlightCandidates, toggleHighlightCandidates);

    // Show/hide verbs that are not interesting
    var showLink = $('<a/>').text('[+]').prop('href', '#').click(toggleHideShow);
    $('.evaluate').append(showLink);


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

    // Edit all editable fields
    $('.vnclass_editable').each(function() {
        $(this).inedit({'onEnd': edited_class_field});
    });

    $('.frame_editable').each(function() {
        $(this).inedit({'onEnd': edited_frame_field});
    });

    // Operations on frames/framesets
    $('.remove_frame').click(function() {
        var vn_class_article = $(this).closest("article")[0];
        var vn_class_id = $(vn_class_article).find("h2").attr("id");

        var frame_div = $(this).closest(".frame")[0];
        var frame_id = $(frame_div).data("frameid");

        $.ajax({
            url: '/remove/',
            type: 'POST',
            data: {
                model: 'VerbNetFrame',
                vn_class: vn_class_id,
                frame_id: frame_id,
                syntax: $(frame_div).find("span[data-field='syntax']").text()
            }
        });

        return false;
    });

});

