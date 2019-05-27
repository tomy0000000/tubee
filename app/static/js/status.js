function onSuccess(responseData, row_tag) {
    console.log(responseData)
    var state = responseData.state;
    if (state === "verified") {
        var badge = $("<span></span>").addClass("badge badge-success").text(state);
        row_tag.children("#state").empty().append(badge);
    } else if (state === "expired") {
        var badge = $("<span></span>").addClass("badge badge-danger").text(state);
        row_tag.children("#state").empty().append(badge);
    } else if (state === "unverified") {
        var badge = $("<span></span>").addClass("badge badge-info").text(state);
        row_tag.children("#state").empty().append(badge);
    } else if (state === "unsubscribed") {
        var badge = $("<span></span>").addClass("badge badge-secondary").text(state);
        row_tag.children("#state").empty().append(badge);
    } else {
        row_tag.children("#state").text(state);
    }
    row_tag.children("#expire").text(responseData.expiration);
    row_tag.children("#last_notification").text(responseData.last_notification);
    row_tag.children("#last_notification_error").text(responseData.last_notification_error);
    row_tag.children("#last_challenge").text(responseData.last_challenge);
    row_tag.children("#last_challenge_error").text(responseData.last_challenge_error);
    var sub_badge = $("<span></span>").addClass("badge badge-success").text(responseData.last_subscribe);
    var unsub_badge = $("<span></span>").addClass("badge badge-warning").text(responseData.last_unsubscribe);
    row_tag.children("#last_request").empty().append(sub_badge, unsub_badge);
    row_tag.children("#stat").text(responseData.stat);
}

function onFailed(responseData, data) {
    console.log("Request Failed");
}

$(document).ready(function() {
    var responseHTML;
    $(".channel").each(function() {
        channel_id = $(this).attr("data-channel-id")
        callback_endpoint = $(this).attr("data-callback-endpoint")
        api_endpoint = $(this).attr("data-api-endpoint")
        // console.log(channel_id)
        data = {
            // "hub.callback": window.location.protocol + "//" + window.location.host + "/Tubee/" + channel_id + "/callback",
            "hub.callback": callback_endpoint,
            "hub.topic": "https://www.youtube.com/xml/feeds/videos.xml?channel_id=" + channel_id,
            "hub.secret": ""
        }
        var row_tag = $(this);
        $.ajax({
            type: "get",
            // data: data,
            // url: "/Tubee/static/php/status.php",
            url: api_endpoint,
        }).done(function(responseData) {
            onSuccess(responseData, row_tag);
        }).fail(function(responseData) {
            onFailed(responseData, data);
        }).always(function(responseData) {
            console.log("Request Sent");
        });
    });
});