function doAlert(text) {
    var clone = $("#alert").clone();
    $("#buttons").after(clone);
    clone.children('p').html(text)
    clone.show();
}

function reboot() {
    $.post('/command',
            {'command':'reboot'},
            function() {
                $('#reboot-modal').modal('hide');
                doAlert('Rebooting...');
            }
          );
}

function poweroff() {
    $.post('/command',
            {'command':'poweroff'},
            function() {
                $('#poweroff-modal').modal('hide');
                doAlert('Shutting down...');
            }
          );
}

$(document).ready(function() {
    $("#reboot-yes").click(reboot);
    $("#poweroff-yes").click(poweroff);
});
