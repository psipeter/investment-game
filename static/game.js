$(function() {  //on page load

    // globals
    let maxUser = 0;
    let maxAgent = 0;
    let turnTime = 1000;
    let startTime = performance.now();
    let endTime = performance.now();
    if (userRole == "A") {
        maxUser = capital;
        maxAgent = 0;  // updated after user moves
    }
    else {
        maxAgent = capital;
        maxUser = initialAgentMove*matchFactor;  // updated after agent moves
    }

    // Hide final page content
    $("#end").hide();
    $(".finalScore").hide();

    // Create the slider
    $("#form").slider({
        create: function() {constrainSliderUser();},
        slide: function(event, ui) {
            let leftHandle;
            let rightHandle;
            if (userRole == "A") {
                leftHandle = $("#userReward")
                rightHandle = $("#agentReward")
            }
            else {
                leftHandle = $("#agentReward")
                rightHandle = $("#userReward")
            }
            let sendLeft = maxUser - ui.value;
            let sendRight = ui.value;
            leftHandle.text("+"+sendLeft);
            rightHandle.text("+"+sendRight);
        }
    });

    // Constrain slider to legal moves
    function constrainSliderUser() {
        $("#form").slider("option", 'max', maxUser);
        if (userRole == "A") {
            $("#userReward").text("+"+maxUser);
            $("#agentReward").text("+"+0);
            $("#form").slider("option", 'value', 0);
        }
        else {
            $("#agentReward").text("+"+0);
            $("#userReward").text("+"+maxUser);
            $("#form").slider("option", 'value', maxUser); // RTL
        }
    }
    function constrainSliderAgent(agentMove) {
        $("#form").slider("option", 'value', 0);
        $("#form").slider("option", 'max', maxAgent);
        let i = 0;
        function recursiveSlide() {
            setTimeout(function() {
                if (userRole == "B") {
                    $("#form").slider("option", 'value', i);
                    $("#agentReward").text("+"+(maxAgent-i));
                    $("#userReward").text("+"+i);
                }
                else {
                    $("#form").slider("option", 'value', (maxAgent-i));
                    $("#agentReward").text("+"+i);
                    $("#userReward").text("+"+(maxAgent-i));                    
                }
                i++;
                if (i<=agentMove) {recursiveSlide();}
            }, turnTime/maxAgent);
        }        
        setTimeout(recursiveSlide, 500);
    }

    function animateAgent(agentMove, data=null) {
        constrainSliderAgent(agentMove); // takes turnTime
        // prepare DOM for user's next move
        setTimeout(function() {
            $("#agentMoves").text($("#agentMoves").text()+agentMove+",")
            $("#submit").show();
            $("#whoseMove").replaceWith("<p id='whoseMove'>Your Move</p>");
            constrainSliderUser();
            startTime = performance.now()
            if (data){gameComplete(data);}
        }, turnTime+1000); //activates 1s after turnTime
    }

    // Update models and DOM when "send" button is pressed
    function getUserMove() {
        let userMove = $("#form").slider("option", "value");
        if (userRole == "A") {
            maxAgent = userMove*matchFactor // update global
            return userMove;
        }
        else {
            return maxUser - userMove; // RTL
        }
    }

    // called when user submits a move
    $("#submit").click(function callUpdate() {
        endTime = performance.now()
        let userTime = (endTime-startTime);
        let userMove = getUserMove();
        $("#userMoves").text($("#userMoves").text()+userMove+",")
        $("#submit").hide();
        $("#whoseMove").replaceWith("<p id='whoseMove'>Opponent Move</p>");
        let form = $("#form");
        let moveData = $('<input type="hidden" name="userMove"/>').val(userMove);
        let timeData = $('<input type="hidden" name="userTime"/>').val(userTime);
        form.append(moveData);
        form.append(timeData);
        let data = form.serialize();
        $.ajax({
            method: 'POST',
            url: $("#submit").attr("updateURL"),
            data: data,
            dataType: 'json',
            success: function (data) {
                let agentMove = data.agentMove;
                let complete = data.complete
                if (complete) {
                    // animate agent's final choice, includes delayed gameComplete
                    if (userRole == "A") {animateAgent(agentMove, data);}
                    else {gameComplete(data);}
                }
                else {
                    if (userRole == "B") {maxUser = matchFactor*agentMove;}
                    animateAgent(agentMove);
                }
            }
        });
        return false;
    });

    // Final page after game is complete
    function gameComplete(data) {
        $("#whoseMove").hide();
        let cU;
        let cA;
        if (userRole == "A") {
            cU = "user left";
            cA = "agent right";
        }
        else {
            cU = "user right";
            cA = "agent left";
        }
        let sU = '<p class="'+cU+'">'+data.userScore+'</p>';
        let sA = '<p class="'+cA+'">'+data.agentScore+'</p>';
        let sO = '<p class="gameOver">Game Over</p>';
        $(".finalScore").show();
        $(".user").replaceWith(sU);
        $("#form").replaceWith(sO);
        $(".agent").replaceWith(sA);
        $("#end").show();
    }
    


    // animate agent's first choice
    if (userRole == "B") {
        $("#whoseMove").replaceWith("<p id='whoseMove'>Opponent Move</p>");
        animateAgent(initialAgentMove);
    }

});  // document load end