// zoom thumbnails to full size
jQuery(function($) {
    $('.thumbzoom img').prepOverlay({
        subtype: 'image',
        urlmatch: '_(thumb|preview)$',
        urlreplace: ''
    });
});

