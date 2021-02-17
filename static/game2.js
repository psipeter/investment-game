$(function() {  //on page load

    // Initialization and globals
    let maxUser;
    let maxAgent;
    let agentTime = 2000;
    let animateTime = 1000;
    let startTime = performance.now();
    let endTime = performance.now();
    let doneGames = false
    let message = null
    let lastKeep = 0;
    complete = false
    // initial game conditions (if continued or agent moves first)
    function strToNum(arr){
        let numArr = [];
        for (i=0; i<arr.length; i++) {
            if (arr[i]=="") {continue;}
            numArr.push(Number(arr[i]));
        }
        return numArr;
    }
    userGives = strToNum(userGives.slice(1, -1).split(", "));
    userKeeps = strToNum(userKeeps.slice(1, -1).split(", "));
    userRewards = strToNum(userRewards.slice(1, -1).split(", "));
    agentGives = strToNum(agentGives.slice(1, -1).split(", "));
    agentKeeps = strToNum(agentKeeps.slice(1, -1).split(", "));
    agentRewards = strToNum(agentRewards.slice(1, -1).split(", "));
    if (userRole == "A") {
        maxUser = capital;
        maxAgent = 0;  // updated after user moves
        $("#nameA").text("You");
        $("#nameB").text("Them");
        // $("#slider").css('background', $("#aNow").css('color'));
        $("#submit").prop('disabled', true);
        $("#loading").hide();
    }
    else {
        $("#nameB").text("You");
        $("#nameA").text("Them");
        // $("#slider").css('background', $("#bNow").css('color'));
        maxAgent = capital;
        maxUser = 0;  // updated after agent moves
        $("#transfer").hide();
        $("#loading").show();
        // $("#submit").css('visibility', 'hidden');
        // $("#loading").css('visibility', 'visible');
    }
    $("#form").slider({
        slide: function(event, ui) {
            $("#submit").prop('disabled', false);
            $("#sendA").css('visibility', 'visible');
            $("#sendB").css('visibility', 'visible');
            $("#sendA").text("$"+(maxUser-ui.value));
            $("#sendB").text("$"+ui.value);
        }
    });
    $("#home").hide();
    $("#flair").hide();
    $("#play-again").hide();
    $("#form").slider({"disabled": true});
    $("#sendA").css('visibility', 'hidden');
    $("#sendB").css('visibility', 'hidden');
    $("#form").slider("option", 'max', capital);
    $("#form").slider("option", 'value', capital/2);
    animateAvailable("capital");
    // switch after animation time
    setTimeout(function() {
        if (userRole == "A") {switchToUser();}
        else {switchToAgent();}
    }, animateTime);


    // Change view after the user or agent moves
    function switchToUser() {
        $("#loading").hide();
        $("#transfer").show();
        $("#form").css('visibility', 'visible');
        $("#slider").css('visibility', 'visible');      
        $("#submit").css('visibility', 'visible');
        $("#form").slider({"disabled": false});
        if (userRole=="B"){
            maxUser = match*agentGives[agentGives.length-1];
        }
        if (maxUser>0) {
            $("#submit").prop('disabled', true);
            $("#sendA").css('visibility', 'hidden');
            $("#sendB").css('visibility', 'hidden');
            $("#form").slider("option", 'max', maxUser);
            $("#form").slider("option", 'value', maxUser/2);
        }
        else {
            $("#submit").prop('disabled', false);
            $("#sendA").css('visibility', 'visible');
            $("#sendB").css('visibility', 'visible');
            $("#sendA").text("$0");
            $("#sendB").text("$0");
            $("#form").slider("option", 'max', 0);
            $("#form").slider("option", 'value', 0);  
            $("#slider").css('visibility', 'hidden');      
        }
        startTime = performance.now()  // track user response time
    }

    function switchToAgent() {
        $("#loading").hide();
        $("#transfer").show();
        $("#sendA").css('visibility', 'visible');
        $("#sendB").css('visibility', 'visible');
        let agentRole = "A";
        let agentGive = agentGives[agentGives.length-1];
        let agentKeep = agentKeeps[agentKeeps.length-1]
        if (userRole == "A") {
            $("#sendA").text(agentGive);
            $("#sendB").text(agentKeep);
            $("#form").slider("option", 'value', agentKeeps[agentKeeps.length-1]);
            agentRole = "B";
        }
        else {
            $("#sendA").text(agentKeep);
            $("#sendB").text(agentGive);
            $("#form").slider("option", 'value', agentGives[agentGives.length-1]);
        }
        $("#form").slider("option", 'max', maxAgent);
        $("#form").slider({"disabled": true});
        $("#form").css('visibility', 'visible');            
        $("#slider").css('visibility', 'visible');      
        $("#submit").css('visibility', 'hidden');
        animateAvailable(agentRole, agentGive, agentKeep)
        // switch to user after animation time
        setTimeout(function() {
            if (complete & userRole=="A") {gameOver();}
            switchToUser();
        }, animateTime);
    }

    function switchToLoading() {
        $("#loading").show();
        $("#transfer").hide();
    }

    function getUserMove() {
        let slideVal = $("#form").slider("option", "value");
        let userGive;
        let userKeep;
        if (userRole == "A") {
            userGive = slideVal;
            userKeep = maxUser - userGive;
            maxAgent = userGive * match // update global
        }
        else {
            userGive = maxUser - slideVal;
            userKeep = maxUser - userGive;
        }
        userGives.push(userGive);
        userKeeps.push(userKeep);
        return [userGive, userKeep];
    }


    // Communicate with the server through AJAX (views.updateGame())
    $("#submit").click(function callUpdate() {
        endTime = performance.now() // track user response time
        let moves = getUserMove();
        $("#submit").prop('disabled', true);
        $("#submit").css('visibility', 'hidden');
        $("#sendA").css('visibility', 'hidden');
        $("#sendB").css('visibility', 'hidden');
        let userGive = moves[0];
        let userKeep = moves[1];
        let userTime = (endTime-startTime);
        if (userRole=="A") {
            $("#aNow").text("$"+userKeep);
            $("#bNow").text("$"+(match*userGive));    
        }
        else {
            $("#aNow").text("$"+(agentKeeps[agentKeeps.length-1]+userGive));
            $("#bNow").text("$"+userKeep);
        }
        animateAvailable(userRole, userGive, userKeep);
        // switch immediately to loading
        switchToLoading();
        let form = $("#form");
        let giveData = $('<input type="hidden" name="userGive"/>').val(userGive);
        let keepData = $('<input type="hidden" name="userKeep"/>').val(userKeep);
        let timeData = $('<input type="hidden" name="userTime"/>').val(userTime);
        form.append(giveData);
        form.append(keepData);
        form.append(timeData);
        let sendData = form.serialize();
        $.ajax({
            method: 'POST',
            url: $("#submit").attr("updateURL"),
            data: sendData,
            dataType: 'json',
            success: function (returnData) {
                // update globals
                userGives = strToNum(returnData.userGives.slice(1, -1).split(", "));
                userKeeps = strToNum(returnData.userKeeps.slice(1, -1).split(", "));
                userRewards = strToNum(returnData.userRewards.slice(1, -1).split(", "));
                agentGives = strToNum(returnData.agentGives.slice(1, -1).split(", "));
                agentKeeps = strToNum(returnData.agentKeeps.slice(1, -1).split(", "));
                agentRewards = strToNum(returnData.agentRewards.slice(1, -1).split(", "));
                complete = returnData.complete;
                doneGames = returnData.doneGames;
                message = returnData.message;
                let wait = (userRole=="A") ? animateTime+agentTime : 2*animateTime+agentTime;
                setTimeout(function () {switchToAgent();}, wait);
                if (complete & userRole=="B") {
                    setTimeout(function () {gameOver();}, animateTime);
                }
            }
        });
        return false;
    });


    // Animate numbers and images changing
    function animateAvailable(move, give=null, keep=null){
        if (move=="capital") {
            $("#aNow").text("$"+capital);
            $("#bNow").text("$0");
            let cap = $("#aNow").clone();
            cap.text("$"+capital)
            cap.attr("id", "animated")
            cap.appendTo("body");
            cap.animate({
                'margin-left' : "+=35%",
                'opacity': 0,
                }, animateTime,
                function() {cap.remove();});
            // setTimeout(animateTime, function() {cap.remove();})
        }
        if (move=="A"){
            lastKeep = keep;
            $("#aNow").text("$"+keep);
            $("#bNow").text("$"+3*give);
            let toB = $("#aNow").clone();
            toB.text("$"+give)
            toB.attr("id", "animated")
            toB.css("margin-left", "60%")
            toB.appendTo("body");
            toB.animate({
                'margin-left': "+=170%",
                'color': $("#bNow").css('color'),
                'opacity': 0,
                }, animateTime,
                function() {toB.remove();});
            let matchB = $("#bNow").clone();
            matchB.text("$"+2*give)
            matchB.attr("id", "animated")
            matchB.css("margin-left", "100%")
            matchB.appendTo("body");
            matchB.animate({
                'margin-left': "-=35%",
                'opacity': 0,
                }, animateTime,
                function() {matchB.remove();});
        }
        if (move=="B") {
            $("#aNow").text("$"+(lastKeep+give));
            $("#bNow").text("$"+keep);
            let toA = $("#bNow").clone();
            toA.text("$"+give)
            toA.attr("id", "animated")
            toA.css("margin-left", "30%")
            toA.appendTo("body");
            toA.animate({
                'margin-left': "-=170%",
                'color': $("#aNow").css('color'),
                'opacity': 0,
                }, animateTime,
                function() {
                    toA.remove();
                    animateTotal();
                    setTimeout(function() {
                        animateAvailable('capital');}, animateTime);
                    });
        }
    }

    function animateTotal() {
        let userScore = userRewards.reduce((a, b) => a + b, 0);
        let agentScore = agentRewards.reduce((a, b) => a + b, 0);
         if (userRole == "A") {
            $("#aTotal").text("$"+userScore);
            $("#bTotal").text("$"+agentScore);
        }
        else {
            $("#aTotal").text("$"+agentScore);
            $("#bTotal").text("$"+userScore);
        }
        let mMid = $("#aNow").css('margin-top');
        let upA = $("#aNow").clone();
        $("#aNow").text("$0");
        upA.css("margin-top", mMid)
        upA.css("width", "10%")
        upA.css("margin-left", "45%")
        upA.appendTo("body");
        upA.animate({
            'margin-top': "-=15%",
            'opacity': 0,
            }, animateTime,
            function() {upA.remove();});        
        let upB = $("#bNow").clone();
        $("#bNow").text("$0");
        upB.css("margin-top", mMid)
        upB.css("width", "10%")
        upB.css("margin-left", "45%")
        upB.appendTo("body");
        upB.animate({
            'margin-top': "-=15%",
            'opacity': 0,
            }, animateTime,
            function() {upB.remove();});        
    }


    // Final page after game is complete

    function gameOver() {
        $("#loading").hide();
        $("#transfer").hide();
        $("#sendA").hide();
        $("#sendB").hide();
        $("#submit").prop('disabled', true);
        $("#submit").hide();
        $("#slider").hide();
        $("#aNow").hide();
        $("#bNow").hide();
        $("#current").hide();
        $("#transfer").show();
        $("#form").show();
        $("#form").replaceWith("<p id='gameOver'>Game Over</p>");
        $("#total").text('Final Score');
        $("#home").show();
        $("#flair").show();
        $("#play-again").show();
        window.stop();  // less hacky solution?
    }
});  // document load end