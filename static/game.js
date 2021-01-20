$(function() {  //on page load

    // initialization and globals
    let maxUser;
    let maxAgent;
    let turnTime = 500;  // ms
    let startTime = performance.now();
    let endTime = performance.now();
    let userScore = 0;
    let agentScore = 0;
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
    agentGives = strToNum(agentGives.slice(1, -1).split(", "));
    agentKeeps = strToNum(agentKeeps.slice(1, -1).split(", "));
    if (userRole == "A") {
        maxUser = capital;
        maxAgent = 0;  // updated after user moves
    }
    else {
        maxAgent = capital;
        maxUser = 0;  // updated after agent moves
    }
    $("#end").hide();
    $(".finalScore").hide();
    $("#form").slider({
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
    createTable();
    if (userRole == "A") {switchToUser();}
    else {switchToAgent();}

    // Populate the move table
    function createTable() {
        let table = $('<table>').addClass('table');
        table.attr("id", "table");
        let headrow = $('<tr>');
        headrow.attr("id", 'headrow');
        let header = $('<th>');
        header.text("action");
        header.attr("id", "action");
        headrow.append(header);
        // let nCols = Math.max(userGives.length, agentGives.length);
        let nCols = 5;
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
                if (p==0 && i==0 && userRole=="A") {headtext="You kept"; row.addClass('green');}
                if (p==0 && i==0 && userRole=="B") {headtext="They kept"; row.addClass('red');}
                if (p==0 && i==1 && userRole=="A") {headtext="You gave"; row.addClass('black');}
                if (p==0 && i==1 && userRole=="B") {headtext="They gave"; row.addClass('black');}
                if (p==1 && i==0 && userRole=="A") {headtext="They kept"; row.addClass('red');}
                if (p==1 && i==0 && userRole=="B") {headtext="You kept"; row.addClass('green');}
                if (p==1 && i==1 && userRole=="A") {headtext="They gave"; row.addClass('green');}
                if (p==1 && i==1 && userRole=="B") {headtext="You gave"; row.addClass('red');}
                let headcolumn = $('<td>');
                headcolumn.attr("id", 'headcolumn');
                headcolumn.text(headtext);
                row.append(headcolumn);
                let nCols;
                if (p==0 && userRole=="A") {nCols=userGives.length;}
                if (p==0 && userRole=="B") {nCols=agentGives.length;}
                if (p==1 && userRole=="A") {nCols=agentGives.length;}
                if (p==1 && userRole=="B") {nCols=userGives.length;}
                for (j=0; j<nCols; j++) {
                    let column = $('<td>');
                    let give;
                    let keep;
                    if (p==0 && userRole=="A") {give=userGives[j]; keep=userKeeps[j];}
                    if (p==0 && userRole=="B") {give=agentGives[j]; keep=agentKeeps[j];}
                    if (p==1 && userRole=="A") {give=agentGives[j]; keep=agentKeeps[j];}
                    if (p==1 && userRole=="B") {give=userGives[j]; keep=userKeeps[j];}
                    column.addClass('column');
                    column.attr("id", "r"+i+"c"+j);
                    if (i==0) {column.text(keep);}
                    else {column.text(give);}
                    row.append(column);
                }
                table.append(row);
            }
        }
        $("#table").replaceWith(table);
    }

    function switchToUser() {
        createTable();
        $("#whoseMove").text("Your move");
        $("#form").show();
        $("#loader").hide();
        if (userRole=="B"){
            maxUser = match*agentGives[agentGives.length-1];
        }
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
        startTime = performance.now()  // track user response time
    }

    function switchToAgent() {
        $("#form").hide();
        $("#loader").show();
        $("#whoseMove").text("Their Move");
        setTimeout(function() {
            createTable();
            if (complete) {gameComplete();}
            else {switchToUser();}
        }, turnTime);
    }

    // Update models and DOM when "send" button is pressed
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
        createTable();
        return [userGive, userKeep];
    }

    // called when user submits a move
    $("#submit").click(function callUpdate() {
        endTime = performance.now() // track user response time
        let moves = getUserMove();
        let userGive = moves[0];
        let userKeep = moves[1];
        let userTime = (endTime-startTime);
        switchToAgent();
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
                userScore = Number(returnData.userScore);
                agentGives = strToNum(returnData.agentGives.slice(1, -1).split(", "));
                agentKeeps = strToNum(returnData.agentKeeps.slice(1, -1).split(", "));
                agentScore = Number(returnData.agentScore);
                complete = returnData.complete;
                if (complete) {gameComplete();}
                else {switchToAgent();}
            }
        });
        return false;
    });

    // Final page after game is complete
    function gameComplete(pause=true) {
        $("#loader").hide();
        $("#form").hide();
        if (userRole=="A" && pause) {
            $("#loader").show();
            $("#whoseMove").show();
            $("#whoseMove").text("Their Move");
            setTimeout(function() {
                createTable();
                gameComplete(pause=false);
            }, turnTime);
        }
        else {
            $("#whoseMove").hide();
            $("#end").show();
            $(".user").text(userScore);
            $(".user").addClass("user");
            $(".agent").text(agentScore);
            $(".agent").addClass("agent");
            $("#form").replaceWith('<p class="gameOver">Game Over</p>');
            if (userRole == "A") {
                $(".leftPlayer").text("Your Score");
                $(".rightPlayer").text("Opponent Score");
                $(".user").addClass("left");
                $(".agent").addClass("right");
            }
            else {
                $(".leftPlayer").text("Opponent Score");
                $(".rightPlayer").text("Your Score");
                $(".user").addClass("right");
                $(".agent").addClass("left");
            }
        }
    }

});  // document load end