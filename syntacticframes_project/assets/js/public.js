function show_plus() {
    // Show/hide verbs that are not interesting
    var showLink = $('<a/>').attr('class', 'plus_link').text('[montrer]').prop('href', '#');
    $('.translations a.pluslink').remove();
    $('.translations').each(function() {
        if ($(this).find('span').size() > 0) {
            if (window._user_authenticated) {
                // insert before the 'add a manual translation' link
                showLink.clone().insertBefore($(this).find('span.new_translation'));
            } else {
                // insert at the end
                $(this).append(showLink.clone());
            }
        }
    });
}


/* Hide dark/gray translations */
function toggleHideShow(e) {
    e.preventDefault();
    $(this).parent().find('[data-hidden=1]').toggle();
    $(this).text($(this).text() == '[montrer]' ? '[cacher]' : '[montrer]');
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
    $(this).closest('.subclass').find('span.translation').each(function() {
        if ($(this).data('origin').split(',').indexOf(origin) != -1) {
            $(this).toggleClass('hover');
        }
    });
}

$(document).ready(function() {
    // Show relation between verbs and origin
    $(document).on('mouseenter mouseleave', 'span.translation', toggleHighlightMembers);
    $(document).on('mouseenter mouseleave', '.members span', toggleHighlightCandidates);

    // Show dark/gray verbs
    show_plus();
    // Clicking on [montrer] always toggles verbs
    $(document).on("click", ".plus_link", toggleHideShow);
});
