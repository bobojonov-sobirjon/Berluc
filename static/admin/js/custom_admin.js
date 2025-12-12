// Custom admin JS for field widths and heights
(function($) {
    $(document).ready(function() {
        // Textarea fieldlar uchun
        $('textarea[name*="description"]').css({
            'width': '70%',
            'height': '100px',
            'min-height': '100px'
        });
        
        $('textarea[name*="short_description"]').css({
            'width': '70%',
            'height': '80px',
            'min-height': '80px'
        });
        
        // CharField fieldlar uchun
        $('input[type="text"][name*="name"], input[type="text"][name*="brand"], input[type="text"][name*="country"], input[type="text"][name*="material"], input[type="text"][name*="position"], input[type="text"][name*="title"], input[type="text"][name*="keywords"]').css({
            'width': '70%'
        });
    });
})(django.jQuery);

