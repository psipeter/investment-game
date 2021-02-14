$(function() {  //on page load
    N_REQUIRED = Number(N_REQUIRED)  // string to number
    N_BONUS = Number(N_BONUS)
    nRequired = Number(nRequired)
    nBonus = Number(nBonus)
    let doneConsentBool = (doneConsent != "None") ? true : false;  // convert string to bool
    let doneSurveyBool = (doneSurvey != "None") ? true : false;
    let doneTutorialBool = (doneTutorial != "None") ? true : false;
    let doneRequiredBool = (doneRequired != "None") ? true : false;
    let doneBonusBool = (doneBonus != "None") ? true : false;
    let doneCashBool = (doneCash != "None") ? true : false;
    console.log(nRequired, doneRequired)

    // Set background colors and activation for each cell

    $('#information-link').addClass('green');
    $("#information-link").hover(
        function() {
            $("#information-bg").addClass("fg");
            $("#information-bg").removeClass("bg");
        }, function() {
            $("#information-bg").addClass("bg");
            $("#information-bg").removeClass("fg");
        }
    );  

    $('#consent-link').addClass('green');
    $("#consent-link").hover(
        function() {
            $("#consent-bg").addClass("fg");
            $("#consent-bg").removeClass("bg");
        }, function() {
            $("#consent-bg").addClass("bg");
            $("#consent-bg").removeClass("fg");
        }
    );  

    if (doneSurveyBool) {
        $('#survey-link').addClass('green');
    }
    else {
        $('#survey-link').addClass('yellow');
    }
    $("#survey-link").hover(
        function() {
            $("#survey-bg").addClass("fg");
            $("#survey-bg").removeClass("bg");
        }, function() {
            $("#survey-bg").addClass("bg");
            $("#survey-bg").removeClass("fg");
        }
    ); 

    if (doneTutorialBool) {
        $('#tutorial-link').addClass('green');
        $('#tutorial-count').addClass('green-flat');
        // $('#tutorial-count').text("1/1");
        $('#tutorial-count').text('complete');
    }
    else {
        if (doneSurveyBool) {
            $('#tutorial-link').addClass('yellow');
            $('#tutorial-count').addClass('yellow-flat');
            // $('#tutorial-count').text("0/1");
            $('#tutorial-count').text("incomplete");
        }
        else {
            $('#tutorial-link').addClass('gray');
            $('#tutorial-count').addClass('gray');
            $('#tutorial-link').removeAttr('href');
            // $('#tutorial-count').text("0/1");            
            $('#tutorial-count').text("incomplete");            
        }
    }
    if (doneSurveyBool){
        $("#tutorial-link").hover(
            function() {
                $("#tutorial-bg").addClass("fg");
                $("#tutorial-bg").removeClass("bg");
            }, function() {
                $("#tutorial-bg").addClass("bg");
                $("#tutorial-bg").removeClass("fg");
            }
        );  
    }

    if (doneRequiredBool) {
        $('#required-link').addClass('green-flat');
        $('#required-count').addClass('green-flat');
        $('#required-link').removeAttr('href');
        $('#required-count').text('complete');
    }
    else {
        if (doneTutorialBool) {
            $('#required-count').addClass('yellow-flat');
            $('#required-count').text(nRequired+"/"+N_REQUIRED);
            $('#required-link').addClass('yellow');
            $("#required-link").hover(
                function() {
                    $("#required-bg").addClass("fg");
                    $("#required-bg").removeClass("bg");
                }, function() {
                    $("#required-bg").addClass("bg");
                    $("#required-bg").removeClass("fg");
                }
            );        
        }
        else {
            $('#required-link').addClass('gray');
            $('#required-count').addClass('gray');
            $('#required-link').removeAttr('href');
            $('#required-count').text('incomplete');
        }
    }

    if (doneBonusBool) {
        $('#bonus-link').addClass('green');
        $('#bonus-count').addClass('green-flat');
        $('#bonus-link').removeAttr('href');
        $('#bonus-count').text('complete');
    }
    else {
        if (doneRequiredBool) {
            $('#bonus-link').addClass('yellow');
            $('#bonus-count').addClass('yellow-flat');
            $('#bonus-count').text(nBonus+"/"+N_BONUS);
            $("#bonus-link").hover(
                function() {
                    $("#bonus-bg").addClass("fg");
                    $("#bonus-bg").removeClass("bg");
                }, function() {
                    $("#bonus-bg").addClass("bg");
                    $("#bonus-bg").removeClass("fg");
                }
            ); 
        }
        else {
            $('#bonus-link').addClass('gray');            
            $('#bonus-count').addClass('gray');            
            $('#bonus-link').removeAttr('href');
            $('#bonus-count').text('incomplete');
        }
    }

    if (doneCashBool) {
        $('#cash-out-link').addClass('green');
        $("#cash-out-link").hover(
            function() {
                $("#cash-bg").addClass("fg");
                $("#cash-bg").removeClass("bg");
            }, function() {
                $("#cash-bg").addClass("bg");
                $("#cash-bg").removeClass("fg");
            }
        );  
    }
    else {
        if (doneSurveyBool & doneTutorialBool & doneRequiredBool) {
            $('#cash-out-link').addClass('yellow');
            $("#cash-out-link").hover(
                function() {
                    $("#cash-bg").addClass("fg");
                    $("#cash-bg").removeClass("bg");
                }, function() {
                    $("#cash-bg").addClass("bg");
                    $("#cash-bg").removeClass("fg");
                }
            );  
        }
        else {
            $('#cash-out-link').addClass('gray');            
            $('#cash-out-link').removeAttr('href');
        }
    }


    $("#stats-link").hover(
        function() {
            $("#stats-bg").addClass("fg");
            $("#stats-bg").removeClass("bg");
        }, function() {
            $("#stats-bg").addClass("bg");
            $("#stats-bg").removeClass("fg");
        }
    );

    $('#feedback-link').addClass('blue');
    $("#feedback-link").hover(
        function() {
            $("#feedback-bg").addClass("fg");
            $("#feedback-bg").removeClass("bg");
        }, function() {
            $("#feedback-bg").addClass("bg");
            $("#feedback-bg").removeClass("fg");
        }
    );  


});  // document load end