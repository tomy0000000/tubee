// function onSuccess(responseData) {
//     console.log(responseData)
//     var state = responseData.state;
//     if (state === "verified") {
//         var badge = $("<span></span>").addClass("badge badge-success").text(state);
//         $("#state").empty().append(badge);
//     } else if (state === "expired") {
//         var badge = $("<span></span>").addClass("badge badge-danger").text(state);
//         $("#state").empty().append(badge);
//     } else if (state === "unverified") {
//         var badge = $("<span></span>").addClass("badge badge-info").text(state);
//         $("#state").empty().append(badge);
//     } else if (state === "unsubscribed") {
//         var badge = $("<span></span>").addClass("badge badge-secondary").text(state);
//         $("#state").empty().append(badge);
//     } else {
//         $("#state").text(state);
//     }
//     $("#expiration").text(responseData.expiration);
//     $("#last-notification").text(responseData.last_notification);
//     $("#last-notification-error").text(responseData.last_notification_error);
//     $("#last-challenge").text(responseData.last_challenge);
//     $("#last-challenge-error").text(responseData.last_challenge_error);
//     $("#last-subscribe").text(responseData.last_subscribe);
//     $("#last-unsubscribe").text(responseData.last_unsubscribe);
//     $("#stat").text(responseData.stat);
// }

$(document).ready(function() {
    $.ajax({
        type: "get",
        url: $("#status-grid").attr("data-api-endpoint"),
    }).done(function(responseData) {
        console.log(responseData)
        var state = responseData.state;
        if (state === "verified") {
            var badge = $("<span></span>").addClass("badge badge-success").text(state);
            $("#state").empty().append(badge);
        } else if (state === "expired") {
            var badge = $("<span></span>").addClass("badge badge-danger").text(state);
            $("#state").empty().append(badge);
        } else if (state === "unverified") {
            var badge = $("<span></span>").addClass("badge badge-info").text(state);
            $("#state").empty().append(badge);
        } else if (state === "unsubscribed") {
            var badge = $("<span></span>").addClass("badge badge-secondary").text(state);
            $("#state").empty().append(badge);
        } else {
            $("#state").text(state);
        }
        $("#expiration").text(responseData.expiration);
        $("#last-notification").text(responseData.last_notification);
        $("#last-notification-error").text(responseData.last_notification_error);
        $("#last-challenge").text(responseData.last_challenge);
        $("#last-challenge-error").text(responseData.last_challenge_error);
        $("#last-subscribe").text(responseData.last_subscribe);
        $("#last-unsubscribe").text(responseData.last_unsubscribe);
        $("#stat").text(responseData.stat);
    }).fail(function(responseData) {
        console.log("Request Failed");
    }).always(function(responseData) {
        console.log("Request Sent");
    });
});