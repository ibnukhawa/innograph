$(document).ready(function() {
    $("#btn_share").click(function(e) {
        var x = $('#social_share')[0].classList
        
        var triger_toggle = x.value.indexOf('invisible')
        if (triger_toggle >= 0) {
            $('#social_share').removeClass('invisible')
        } else {
            $('#social_share').addClass('invisible')
        }
    });
    $(".facebook-icon").click(function(e) {
        var target = window.location.href
        window.open("https://www.facebook.com/sharer/sharer.php?u="+target, '_blank');
    });
});