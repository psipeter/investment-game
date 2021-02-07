$(function() {  //on page load

    // initialization and globals
    let maxUser;
    let maxAgent;
    let turnTime = 500;  // ms
    let startTime = performance.now();
    let endTime = performance.now();
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
        $('#aReward').addClass('green');
        $('#bReward').addClass('red');
        $('#aScore').addClass('green');
        $('#bScore').addClass('red');
        $('#keep100').addClass('left');
        $('#give100').addClass('right');
        $('#form').css({'background': 'linear-gradient(90deg, green, red)'});
        $("#submit").prop('disabled', true);
        $(".loading-bar").hide();
    }
    else {
        maxAgent = capital;
        maxUser = 0;  // updated after agent moves
        $('#aReward').addClass('red');
        $('#bReward').addClass('green');
        $('#aScore').addClass('red');
        $('#bScore').addClass('green');
        $('#keep100').addClass('right');
        $('#give100').addClass('left');
        $('#form').css({'background': 'linear-gradient(90deg, red, green)'});
        $("#submit").hide();
        $(".loading-bar").show();
    }
    $('#aTitle').css({'background': '#5cf7ff'});
    $('#bTitle').css({'background': 'white'});
    $("#gameOver").hide();
    $("#aScore").hide();
    $("#bScore").hide();
    $("#flair").hide();
    $("#home").hide();
    $("#play").hide();
    $("#form").slider({
        slide: function(event, ui) {
            $("#submit").prop('disabled', false);
            $("#aReward").show();
            $("#bReward").show();
            $("#aReward").text("+"+(maxUser-ui.value));
            $("#bReward").text("+"+ui.value);
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
        let header = $('<th>');
        header.text("turn");
        headrow.append(header);
        // let nCols = Math.max(userGives.length, agentGives.length);
        let nCols = 5;
        for (a=0; a<nCols; a++){
            let header = $('<th>');
            let turnText = "";
            if (a==0) {turnText="I"};
            if (a==1) {turnText="II"};
            if (a==2) {turnText="III"};
            if (a==3) {turnText="IV"};
            if (a==4) {turnText="V"};
            header.text(turnText);
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
        $("#form").show();
        $("#slider").show();      
        $("#submit").show();
        $("#give100").show();
        $("#keep100").show();
        $("#form").slider({"disabled": false});
        if (userRole=="B"){
            $('#aTitle').css({'background': 'white'});
            $('#bTitle').css({'background': '#5cf7ff'});
            maxUser = match*agentGives[agentGives.length-1];
        }
        else {
            $('#aTitle').css({'background': '#5cf7ff'});
            $('#bTitle').css({'background': 'white'});
        }
        if (maxUser>0) {
            $("#submit").prop('disabled', true);
            $("#aReward").hide();
            $("#bReward").hide();
            $("#form").slider("option", 'max', maxUser);
            $("#form").slider("option", 'value', maxUser/2);
        }
        else {
            $("#submit").prop('disabled', false);
            $("#aReward").show();
            $("#bReward").show();
            $("#aReward").text("0");
            $("#bReward").text("0");
            $("#form").slider("option", 'max', 0);
            $("#form").slider("option", 'value', 0);  
            $("#slider").hide();      
        }
        startTime = performance.now()  // track user response time
    }

    function switchToAgent() {
        $("#form").hide();
        $(".loading-bar").show();
        if (userRole == "A") {
            $('#aTitle').css({'background': 'white'});
            $('#bTitle').css({'background': '#5cf7ff'});
        }
        else {
            $('#aTitle').css({'background': '#5cf7ff'});
            $('#bTitle').css({'background': 'white'});
        }
        setTimeout(function() {
            createTable();
            $("#aReward").show();
            $("#bReward").show();
            $(".loading-bar").hide();
            if (userRole == "A") {
                $("#aReward").text(agentGives[agentGives.length-1]);
                $("#bReward").text(agentKeeps[agentKeeps.length-1]);
                $("#form").slider("option", 'value', agentKeeps[agentKeeps.length-1]);
            }
            else {
                $("#aReward").text(agentKeeps[agentKeeps.length-1]);
                $("#bReward").text(agentGives[agentGives.length-1]);
                $("#form").slider("option", 'value', agentGives[agentGives.length-1]);
            }
            $("#form").slider("option", 'max', maxAgent);
            $("#form").slider({"disabled": true});
            $("#form").show();            
            $("#slider").show();      
            if (complete) {gameComplete();}
            else {
                setTimeout(function() {
                    switchToUser();
                }, turnTime);
            }
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
        $("#submit").prop('disabled', true);
        $("#submit").hide();
        $("#aReward").hide();
        $("#bReward").hide();
        $("#give100").hide();
        $("#keep100").hide();
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
                userRewards = strToNum(returnData.userRewards.slice(1, -1).split(", "));
                agentGives = strToNum(returnData.agentGives.slice(1, -1).split(", "));
                agentKeeps = strToNum(returnData.agentKeeps.slice(1, -1).split(", "));
                agentRewards = strToNum(returnData.agentRewards.slice(1, -1).split(", "));
                complete = returnData.complete;
                if (complete) {gameComplete();}
                else {switchToAgent();}
            }
        });
        return false;
    });

    // Final page after game is complete
    function gameComplete(pause=true) {
        $(".loading-bar").hide();
        $("#form").hide();
        if (userRole=="A" && pause) {
            $(".loading-bar").show();
            setTimeout(function() {
                createTable();
                gameComplete(pause=false);
            }, turnTime);
        }
        else {
            $("#form").hide();
            $("#aReward").hide();
            $("#bReward").hide();
            $("#give100").hide();
            $("#keep100").hide();
            $("#submit").hide();
            $("#submit").prop('disabled', true);
            $("#gameOver").show();
            $("#flair").show();
            // $("#flair").text();  // randomized text
            $("#home").show();
            $("#play").show();
            let userScore = userRewards.reduce((a, b) => a + b, 0);
            let agentScore = agentRewards.reduce((a, b) => a + b, 0);
            if (userRole == "A") {
                $("#aScore").text(userScore);
                $("#bScore").text(agentScore);
            }
            else {
                $("#aScore").text(agentScore);
                $("#bScore").text(userScore);
            }
            $("#aScore").show();
            $("#bScore").show();
        }
    }
});  // document load end