$(document).ready(function() {
    $("#username").on("keyup", function(event) {
        var name = $("#username").val()
        if (name) {
            $("#headline").text("Welcome, "+name+"!");
        } else {
            $("#headline").text("Welcome!");
        }
    });
});