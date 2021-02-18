$(function() {  // on page load
    let progress = 0;
    let maxProgress = 4;
    let fadeTime = 2000;
    updateMain();  // Fade in first page

    // Redirect on click
    $('#next').click(function(e) {
        updateProgress();
        updateMain();
    });
    $('#back').click(function(e) {
        progress = Math.max(0, progress-1);
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
        $('#t3').fadeOut(0)        
        $('#t4').fadeOut(0)        
        $('#m1').hide();
        $('#m2').hide();
        $('#m3').hide();
        $('#m4').hide();
        $('#m1').children().fadeOut(0);
        $('#m2').children().fadeOut(0);
        $('#m3').children().fadeOut(0);
        $('#m4').children().fadeOut(0);
        resetVals("m2");
        resetVals("m3");
        resetVals("m4");
        // $("#back").prop("disabled", true);
        $("#next").prop("disabled", true);
        if (progress<=0) {main1();}
        if (progress==1) {main2();}
        if (progress==2) {main3();}
        if (progress==3) {main4();}
    }

    // display and timing of main content
    function main1(e) {
        $('#m1').show();
        $('#t1').fadeIn(0)        
        $('#m1a').fadeIn(fadeTime);
        setTimeout(function(){$('#m1b').fadeIn(fadeTime);}, fadeTime);
        setTimeout(function(){$('#m1c').fadeIn(fadeTime);}, 2*fadeTime);
        enableNavigation(3*fadeTime, 1);
    }

    function main2(e) {
        let capital = 10;
        let giveA = 7;
        let keepA = 3;
        let giveB = 10;
        let keepB = 20;
        $('#m2').show();
        $('#t2').fadeIn(0);
        $('#m2a').fadeIn(fadeTime);
        $('.game').fadeIn(0);
        animateCapital(2*fadeTime, "m2",capital);
        setTimeout(function(){$("#m2b1").fadeIn(fadeTime);}, fadeTime);
        animateAToBTutor(4*fadeTime, "m2", giveA, keepA);
        setTimeout(function(){$("#m2b2").fadeIn(fadeTime);}, 3*fadeTime);
        animateAToB(6*fadeTime, "m2", giveA, keepA);
        setTimeout(function(){$("#m2b3").fadeIn(fadeTime);}, 5*fadeTime);
        animateBToA(8*fadeTime, "m2", keepA, giveB, keepB);
        setTimeout(function(){$("#m2b4").fadeIn(fadeTime);}, 7*fadeTime);
        animateTotal(10*fadeTime, "m2", keepA, giveB, keepB)
        setTimeout(function(){$("#m2b5").fadeIn(fadeTime);}, 9*fadeTime);
        setTimeout(function(){$('#m2c').fadeIn(fadeTime);}, 11*fadeTime);
        enableNavigation(12*fadeTime, 2);
    }

    function main3(e) {
        let capital = 10;
        let giveA = 10;
        let keepA = 0;
        let giveB = 15;
        let keepB = 15;
        let giveA2 = 10;
        let keepA2 = 0;
        let giveB2 = 0;
        let keepB2 = 30;
        $('#m3').show();
        $('#t3').fadeIn(0);
        $('#m3a').fadeIn(fadeTime);
        $('.game').fadeIn(0);
        setTimeout(function(){$("#m3c").fadeIn(fadeTime);}, 1*fadeTime);
        animateCapital(2*fadeTime, "m3", capital);
        animateAToB(3*fadeTime, "m3", giveA, keepA);
        animateBToA(4*fadeTime, "m3", keepA, giveB, keepB);
        animateTotal(5*fadeTime, "m3", keepA, giveB, keepB)
        setTimeout(function(){
            resetVals("m3");
            $("#m3c").css('color', 'gray');
            $("#m3d").fadeIn(fadeTime);},
        6*fadeTime);
        animateCapital(7*fadeTime, "m3", capital);
        animateAToB(8*fadeTime, "m3", giveA2, keepA2);
        animateBToA(9*fadeTime, "m3", keepA2, giveB2, keepB2);
        animateTotal(10*fadeTime, "m3", keepA2, giveB2, keepB2)
        setTimeout(function(){
            resetVals("m3");
            $("#m3d").css('color', 'gray');
            $("#m3c").fadeOut(fadeTime);
            $("#m3d").fadeOut(fadeTime);},
        11*fadeTime);
        setTimeout(function(){$("#m3e").fadeIn(fadeTime);}, 12*fadeTime);
        enableNavigation(13*fadeTime, 3);
    }

    function main4(e) {
        let capital = 10;
        let maxUser = capital;
        $('#m4').show();
        $('#t4').fadeIn(0);
        $('#m4a').fadeIn(fadeTime);
        $('.game').fadeIn(0);
        $("#form").slider({
            slide: function(event, ui) {
                $("#submit").prop('disabled', false);
                $("#sendA").css('visibility', 'visible');
                $("#sendB").css('visibility', 'visible');
                $("#sendA").text("$"+(maxUser-ui.value));
                $("#sendB").text("$"+ui.value);
            }
        });
        $("#form").slider("option", 'max', maxUser);
        $("#form").slider("option", 'value', maxUser/2);
        $("#form").slider({"disabled": true});
        $("#sendA").css('visibility', 'hidden');
        $("#sendB").css('visibility', 'hidden');
        animateCapital(fadeTime, "m4", capital);
        setTimeout(function(){
            $("#transfer").fadeIn(fadeTime);
            $("#form").slider({"disabled": false});
            $("#submit").prop('disabled', true);
            $("#m4a").fadeOut(fadeTime);
            $("#m4c").fadeIn(fadeTime);},
        2*fadeTime);
        $("#submit").click(function () {
            let giveA = $("#form").slider("option", "value");
            let keepA = maxUser - giveA;
            let giveB = 0;
            let keepB = 3*giveA;
            $("#submit").prop('disabled', true);
            $("#submit").css('visibility', 'hidden');
            $("#sendA").css('visibility', 'hidden');
            $("#sendB").css('visibility', 'hidden');
            $("#loading").show();
            $("#transfer").hide();
            animateAToB(0, "m4", giveA, keepA);
            $("#m4c").hide();
            $("#m4d").show();
            setTimeout(function() {
                $("#loading").hide();
                $("#transfer").show();
                $("#sendA").css('visibility', 'visible');
                $("#sendB").css('visibility', 'visible');
                $("#sendA").text(giveB);
                $("#sendB").text(keepB);
                $("#form").slider("option", 'value', keepB);
                $("#form").slider("option", 'max', keepB);
                $("#form").slider({"disabled": true});
                $("#form").css('visibility', 'visible');            
                $("#slider").css('visibility', 'visible');      
                $("#submit").css('visibility', 'hidden');
                }, 2*fadeTime);
            animateBToA(2*fadeTime, "m4", keepA, giveB, keepB);
            animateTotal(3*fadeTime, "m4", keepA, giveB, keepB);
            setTimeout(function() {$("#m4d").hide();}, 3*fadeTime);
            setTimeout(function() {$("#m4e").show();}, 3*fadeTime);
            setTimeout(function() {$("#m4e").hide();}, 4*fadeTime);
            setTimeout(function() {$("#m4f").show();}, 4*fadeTime);
            setTimeout(function() {$("#transfer").hide();}, 5*fadeTime);
            enableNavigation(5*fadeTime, 4);
        });


    }




    function animateCapital(timeout, addTo, capital) {
        setTimeout(function(){
            $("#aNow"+addTo).text("$"+capital);
            $("#bNow"+addTo).text("$0");
            let cap = $("#aNow"+addTo).clone();
            cap.attr("id", "cap");
            cap.appendTo("#"+addTo);
            cap.css("margin-left", "0%");
            cap.animate({
                'margin-left' : "+=5%",
                'opacity': 0,
                }, fadeTime,
                function() {cap.remove();});
        }, timeout);
    }
    function animateAToBTutor(timeout, addTo, giveA, keepA) {
        setTimeout(function(){
            $("#aNow"+addTo).text("$"+keepA);
            $("#bNow"+addTo).text("$"+giveA);
            let toB = $("#aNow"+addTo).clone();
            toB.attr("id", "toB");
            toB.text("$"+giveA);
            toB.css("margin-left", "10%");
            toB.appendTo("#"+addTo);
            toB.animate({
                'margin-left': "+=80%",
                'color': $("#bNow"+addTo).css('color'),
                'opacity': 0,
                }, fadeTime,
                function() {toB.remove();});
        }, timeout);
    }
    function animateAToB(timeout, addTo, giveA, keepA) {
        setTimeout(function(){
            let toB = $("#aNow"+addTo).clone();
            $("#aNow"+addTo).text("$"+keepA);
            toB.text("$"+giveA);
            toB.attr("id", "toB2");
            toB.css("margin-left", "15%");
            toB.appendTo("#"+addTo);
            toB.animate({
                'margin-left': "+=65%",
                'color': $("#bNow"+addTo).css('color'),
                'opacity': 0,
                }, fadeTime,
                function() {toB.remove();});
            $("#bNow"+addTo).text("$"+3*giveA);
            let matchB = $("#bNow"+addTo).clone();
            matchB.attr("id", "matchB");
            matchB.text("$"+2*giveA);
            matchB.css("margin-left", "100%");
            matchB.appendTo("#"+addTo);
            matchB.animate({
                'margin-left': "-=5%",
                'opacity': 0,
                }, fadeTime,
                function() {matchB.remove();});

        }, timeout);
    }
    function animateBToA(timeout, addTo, keepA, giveB, keepB) {
        setTimeout(function(){
            $("#aNow"+addTo).text("$"+(keepA+giveB));
            let toA = $("#bNow"+addTo).clone();
            toA.attr("id", "toA2");
            $("#bNow"+addTo).text("$"+keepB);
            toA.text("$"+giveB);
            toA.css("width", "10%");
            toA.css("margin-left", "75%");
            toA.appendTo("#"+addTo);
            toA.animate({
                'margin-left': "-=65%",
                'color': $("#aNow"+addTo).css('color'),
                'opacity': 0,
                }, fadeTime,
                function() {
                    toA.remove();
                    // animateTotal();
                    });
        }, timeout);
    }
    function animateTotal(timeout, addTo, keepA, giveB, keepB){
        setTimeout(function(){
            $("#aTotal"+addTo).text("$"+(keepA+giveB));
            $("#bTotal"+addTo).text("$"+keepB);
            let upA = $("#aNow"+addTo).clone();
            upA.attr("id", "upA");
            upA.text("$"+(keepA+giveB));
            $("#aNow"+addTo).text("$0");
            upA.appendTo("#"+addTo);
            upA.animate({
                'margin-top': "-=5%",
                'opacity': 0,
                }, fadeTime,
                function() {upA.remove();});        
            let upB = $("#bNow"+addTo).clone();
            upB.attr("id", "upB");
            upB.text("$"+keepB);
            $("#bNow"+addTo).text("$0");
            upB.appendTo("#"+addTo);
            upB.animate({
                'margin-top': "-=5%",
                'opacity': 0,
                }, fadeTime,
                function() {upB.remove();});
        }, timeout);
    }



    function resetVals(addTo) {
        $("#aNow"+addTo).text("$0");
        $("#bNow"+addTo).text("$0");
        $("#aTotal"+addTo).text("$0");
        $("#bTotal"+addTo).text("$0");
    }

    function enableNavigation(timeout, prog) {
         setTimeout(function(){
            $("#back").prop("disabled", false);
            $("#next").prop("disabled", false);
            progress = prog;
        }, timeout);
    }

});  // document load end