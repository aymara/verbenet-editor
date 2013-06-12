/* Project specific Javascript goes here. */

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

function toggleHighlightMembers() {
    var origins = $(this).data('origin').split(',');
    $('.verbnet_members li').each(function() {
        if (origins.indexOf($(this).text()) != -1) {
            $(this).toggleClass('hover');
        }
    });
}

function toggleHighlightCandidates() {
    var origin = $(this).text();
    console.log(origin);
    $(this).parent().parent().find('.evaluate li').each(function() {
        if ($(this).data('origin').split(',').indexOf(origin) != -1) {
            $(this).toggleClass('hover');
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

    $('.verb-classes').css('height', 0.9 * $(window).height() + 'px')
});


