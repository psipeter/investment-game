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
    $('#consent-link').addClass('green');

    if (doneSurveyBool) {
        $('#survey-link').addClass('green');
    }
    else {
        $('#survey-link').addClass('yellow');
    }

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

    if (doneRequiredBool) {
        $('#required-link').addClass('green');
        $('#required-count').addClass('green-flat');
        $('#required-link').removeAttr('href');
        $('#required-count').text('complete');
    }
    else {
        if (doneTutorialBool) {
            $('#required-link').addClass('yellow');
            $('#required-count').addClass('yellow-flat');
            $('#required-count').text(nRequired+"/"+N_REQUIRED);
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
    }
    else {
        if (doneSurveyBool & doneTutorialBool & doneRequiredBool) {
            $('#cash-out-link').addClass('yellow');
        }
        else {
            $('#cash-out-link').addClass('gray');            
            $('#cash-out-link').removeAttr('href');
        }
    }

    $('#feedback-link').addClass('blue');

});  // document load end