$(function() {  //on page load

    // globals
    let maxUser = 0;
    let maxAgent = 0;
    let turnTime = 1000;
    let startTime = performance.now();
    let endTime = performance.now();
    let userMoves = [];
    let agentMoves = [];
    let userMovesMax = [];
    let agentMovesMax = [];
    if (userRole == "A") {
        maxUser = Number(capital);
        userMovesMax.push(maxUser);
        maxAgent = 0;  // updated after user moves
    }
    else {
        maxAgent = Number(capital);
        maxUser = initialAgentMove*matchFactor;  // updated after agent moves
        // agentMoves.push(initialAgentMove);
        // agentMovesMax.push(maxAgent);
        // userMovesMax.push(maxUser);
    }

    // Hide final page content
    $("#end").hide();
    $(".finalScore").hide();

    // Populate the move table
    function createTable() {
        console.log("user", userMovesMax);
        console.log("agent", agentMovesMax);
        let table = $('<table>').addClass('table');
        table.attr("id", "table");
        let headrow = $('<tr>');
        headrow.attr("id", 'headrow');
        let header = $('<th>');
        header.text("action");
        header.attr("id", "action");
        headrow.append(header);
        let nCols = Math.max(userMoves.length, agentMoves.length);
        for (a=0; a<nCols; a++){
            let header = $('<th>');
            header.text("turn "+a);
            headrow.append(header);          
        }
        table.append(headrow);
        for (p=0; p<2; p++) {  // two players
            for (i=0; i<2; i++) {  // two rows per player
                let row = $('<tr>').addClass('row');
                let headtext;
                let color1;
                let color2;
                if (p==0 && i==0) {
                    if (userRole=="A") {headtext="You kept"; row.addClass('green');}
                    else {headtext="They kept"; row.addClass('red');}}
                if (p==0 && i==1) {
                    if (userRole=="A") {headtext="You gave"; row.addClass('black');}
                    else {headtext="They gave"; row.addClass('black');}}
                if (p==1 && i==0) {
                    if (userRole=="A") {headtext="They kept"; row.addClass('red');}
                    else {headtext="You kept"; row.addClass('green');}}
                if (p==1 && i==1) {
                    if (userRole=="A") {headtext="They gave"; row.addClass('green');}
                    else {headtext="You gave"; row.addClass('red');}}
                let headcolumn = $('<td>');
                headcolumn.attr("id", 'headcolumn');
                headcolumn.text(headtext);
                row.append(headcolumn);
                let nCols;
                if (p==0 && userRole=="A") {nCols=userMoves.length;}
                if (p==0 && userRole=="B") {nCols=agentMoves.length;}
                if (p==1 && userRole=="A") {nCols=agentMoves.length;}
                if (p==1 && userRole=="B") {nCols=userMoves.length;}
                for (j=0; j<nCols; j++) {
                    let column = $('<td>');
                    let max;
                    let move;
                    if (p==0 && userRole=="A") {max=userMovesMax[j]; move=userMoves[j];}
                    if (p==0 && userRole=="B") {max=agentMovesMax[j]; move=agentMoves[j];}
                    if (p==1 && userRole=="A") {max=agentMovesMax[j]; move=agentMoves[j];}
                    if (p==1 && userRole=="B") {max=userMovesMax[j]; move=userMoves[j];}
                    column.addClass('column');
                    column.attr("id", "r"+i+"c"+j);
                    if (i==0) {column.text(max-move);}
                    else {column.text(move);}
                    row.append(column);
                }
                table.append(row);
            }
        }
        $("#table").replaceWith(table);
    }
    // createTable();  // call once to add element

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
        if (userRole=="A"){
            maxUser = Number(capital);
            userMovesMax.push(maxUser);
        }
        else {
            maxUser = matchFactor*agentMove;
            userMovesMax.push(maxUser);
            agentMovesMax.push(Number(capital));
        }
        constrainSliderAgent(agentMove); // takes turnTime
        // prepare DOM for user's next move
        setTimeout(function() {
            $("#agentMoves").text($("#agentMoves").text()+agentMove+",")
            agentMoves.push(agentMove);
            createTable();
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
        let move;
        if (userRole == "A") {
            maxAgent = userMove*matchFactor // update global
            agentMovesMax.push(maxAgent);
            move = userMove;
        }
        else {
            move = maxUser - userMove; // RTL
        }
        userMoves.push(move);
        return move;
    }

    // called when user submits a move
    $("#submit").click(function callUpdate() {
        endTime = performance.now()
        let userTime = (endTime-startTime);
        let userMove = getUserMove();
        $("#userMoves").text($("#userMoves").text()+userMove+",")
        createTable();
        $("#submit").hide();
        $("#whoseMove").replaceWith("<p id='whoseMove'>Their Move</p>");
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
                let complete = data.complete;
                if (complete) {
                    // animate agent's final choice, includes delayed gameComplete
                    if (userRole == "A") {animateAgent(agentMove, data);}
                    else {gameComplete(data);}
                }
                else {
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
        $("#whoseMove").replaceWith("<p id='whoseMove'>Their Move</p>");
        animateAgent(initialAgentMove);
    }

});  // document load end