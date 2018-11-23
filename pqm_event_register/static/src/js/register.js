$(document).ready(function(){
    $('#event_register_form').on('submit', function(e){
        var form = $('#event_register_form');
        var counter = 0;
        $('#event_register_form select').each(function(){
            counter += $(this).val();
        });
        if(counter < 1){
            e.preventDefault();
        }
    });
});