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

    // Redirect on click
    $('#information-box').click(function(e) {
        window.location.href=$(this).attr("href");
    });

    $('#consent-box').click(function(e) {
        window.location.href=$(this).attr("href");
    });

    $('#survey-box').click(function(e) {
        window.location.href=$(this).attr("href");
    });

    $('#tutorial-box').click(function(e) {
        window.location.href=$(this).attr("href");
    });

    $('#required-box').click(function(e) {
        window.location.href=$(this).attr("href");
    });

    $('#bonus-box').click(function(e) {
        window.location.href=$(this).attr("href");
    });

    $('#stats-box').click(function(e) {
        window.location.href=$(this).attr("href");
    });

    $('#cash-box').click(function(e) {
        window.location.href=$(this).attr("href");
    });

    $('#feedback-box').click(function(e) {
        window.location.href=$(this).attr("href");
    });

    $('#information-text').text('Information [✔]');
    $('#consent-text').text('Consent [✔]');
    if (doneSurveyBool) {
        $('#survey-text').text('Survey [✔]');
    }
    if (doneTutorialBool) {
        $('#tutorial-text').text('Tutorial [✔]');
    }
    if (doneRequiredBool) {
        $('#required-text').text('Required Games [✔]');
    }
    else {
        $('#stats-box').addClass('inactive');
        $('#stats-box').off('click');
        $('#stats-box').click(function(e) {
            alert("To view game statistics, first play more bonus games");
        });
        if (doneTutorialBool) {
            $('#required-text').text(
                "Required Games ["+nRequired+"/"+N_REQUIRED+"]");
            }
        else {
            $('#required-box').addClass('inactive');
            $('#required-box').off('click');
            $('#required-box').click(function(e) {
                alert("To play required games, first complete the tutorial");
            });
        }
    }
    if (doneBonusBool) {
        $('#bonus-text').text('Bonus Games [✔]');
    }
    else {
        if (doneRequiredBool) {
            $('#bonus-text').text(
                "Bonus Games ["+nBonus+"/"+N_BONUS+"]");
        }
        else {
            $('#bonus-box').addClass('inactive');
            $('#bonus-box').off('click');
            $('#bonus-box').click(function(e) {
                alert("To play bonus games, first complete required games");
            });
        }
    }
    if (doneCashBool) {
        $('#cash-text').text('Cash Out [✔]');
    }
    else {
        if (doneSurveyBool & doneTutorialBool & doneRequiredBool) {
            // 
        }
        else {
            $('#cash-box').addClass('inactive');
            $('#cash-box').off('click');
            $('#cash-box').click(function(e) {
                alert("To cash out, first complete the required games,\
                    then play bonus games to earn more rewards");
            });
        }
    }

});  // document load end