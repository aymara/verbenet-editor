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

/* Send change to server after edited in place */
function edited_field(input, label) {
    var new_val = input.val();
    var field = $(label)
    var vn_class = field.parent().attr("id");

    $.ajax({
        url: '/update/',
        type: 'POST',
        data: {vn_class: vn_class, field: field.val(), label: new_val}
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

    // Edit all editable fields
    $('.editable').each(function() {
        $(this).inedit({'onEnd': edited_field});
    });

});

