// Update text of "send" button to reflect value of slider
$("#djangoForm").ready(function moveSlider() {
    $("#submitButton").val("send "+$("#id_userMove").val());
});
$("#djangoForm").change(function moveSlider() {
    $("#submitButton").val("send "+$("#id_userMove").val());
});

// Update models and DOM when "send" button is pressed
$("#submitButton").click(function callUpdate() {
    "use strict";
    let form = $("#djangoForm");
    $.ajax({
        method: 'POST',
        url: form.attr("updateURL"),
        data: form.serialize(),
        dataType: 'json',
        success: function (data) {
            $("#userMove").text(data.userMove);
            $("#agentMove").text(data.agentMove);
            $("#userMoves").text(data.userMoves);
            $("#agentMoves").text(data.agentMoves);
            if (data.complete) {
                $("#playerA").replaceWith('<h2 id="playerA">Final Score:</h2>');
                $("#playerB").replaceWith('<h2 id="playerB">Final Score:</h2>');
                let cU = "";
                let cA = "";
                if (data.userRole == "A"){
                    cU = "user left";
                    cA = "agent right";
                }
                else {
                    cU = "user right";
                    cA = "agent left";
                }
                let sU = '<p class="'+cU+'">'+data.userScore+'</p>';
                let sA = '<p class="'+cA+'">'+data.agentScore+'</p>';
                let sO = '<p class="center">Game Over</p>';
                $(".user").replaceWith(sU);
                $("div.form").replaceWith(sO);
                $(".agent").replaceWith(sA);
                $(document.body).append(
                    "<div class='home-newgame'>\
                        <a href='"+homeURL+"'>Home</a>\
                        <a href='"+gameURL+"'>Play Again</a>\
                    </div>")
            }
        }
    });
    return false;
});