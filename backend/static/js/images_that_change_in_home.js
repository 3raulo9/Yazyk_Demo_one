$(document).ready(function () {
    $.get('/fetch_image', function (data) {
        $('.image').attr('src', data);
    });
});
