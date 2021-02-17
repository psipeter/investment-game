$(function() {  // on page load
    let progress = 0;
    let maxProgress = 2;
    let fadeTime = 200;
    // $('#main1').hide()
    // $('#main1').fadeOut(fadeTime, function() {
    //     $('#test').fadeIn(fadeTime, function() {
    //         // alert("done");
    //         console.log(1);
    //     });
    // });
    updateMain();  // Fade in first page

    // Redirect on click
    $('#next').click(function(e) {
        progress = Math.max(1, progress+1);
        updateProgress();
        updateMain();
    });
    $('#back').click(function(e) {
        progress = Math.min(0, progress-1);
        updateProgress();
        updateMain();
    });

    // update progress bar
    function updateProgress(e) {
        let width = Math.min(100, Math.max(0, 100*progress/maxProgress));
        $("#progress-bar-fg").width(width+"%");
    }

    // load new minipage
    function updateMain(e) {
        $('#t1').fadeOut(0)        
        $('#t2').fadeOut(0)        
        $('#m1').hide();
        $('#m2').hide();
        $('#m1').children().fadeOut(0);
        $('#m2').children().fadeOut(0);
        $("#back").prop("disabled", true);
        $("#next").prop("disabled", true);
        if (progress<=0) {main1();}
        if (progress==1) {main2();}
    }

    // display and timing of main content
    function main1(e) {
        $('#m1').show();
        $('#t1').fadeIn(0)        
        $('#m1a').fadeIn(fadeTime, function() {
            $('#m1b').fadeIn(fadeTime, function() {
                $('#m1c').fadeIn(fadeTime, function() {
                    $("#back").prop("disabled", false);
                    $("#next").prop("disabled", false);
                });
            });
        });
    }

    function main2(e) {
        $('#m2').show();
        $('#t2').fadeIn(0)
        $('#m2a').fadeIn(fadeTime, function() {
            $('#m2b').fadeIn(fadeTime, function() {
                $('#m2c').fadeIn(fadeTime, function() {
                    $("#back").prop("disabled", false);
                    $("#next").prop("disabled", false);
                });
            });
        });
    }

});  // document load end