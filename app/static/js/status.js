function onSuccess(responseData, row_tag) {
    responseHTML = document.createElement("html");
    responseHTML.innerHTML = responseData;
    $(responseHTML).find("dt").each(function(){
        switch($(this).text()) {
            case "State":
                var context = $(this).next().text();
                if (context === "verified") {
                    var badge = $("<span></span>").addClass("badge badge-success").text(context);
                    row_tag.children(".state").empty().append(badge);
                } else if (context === "expired") {
                    var badge = $("<span></span>").addClass("badge badge-danger").text(context);
                    row_tag.children(".state").empty().append(badge);
                } else if (context === "unverified") {
                    var badge = $("<span></span>").addClass("badge badge-info").text(context);
                    row_tag.children(".state").empty().append(badge);
                } else if (context === "unsubscribed") {
                    var badge = $("<span></span>").addClass("badge badge-secondary").text(context);
                    row_tag.children(".state").empty().append(badge);
                } else {
                    row_tag.children(".state").text($(this).next().text());
                }
                break;
            case "Last successful verification":
                row_tag.children(".last_challenge").text($(this).next().text());
                break;
            case "Expiration time":
                row_tag.children(".expire").text($(this).next().text());
                break;
            case "Last subscribe request":
                last_subscribe_request = $(this).next().text();
                row_tag.children(".last_request").text($(this).next().text());
                break;
            case "Last unsubscribe request":
                last_unsubscribe_request = $(this).next().text();
                row_tag.children(".last_request").text($(this).next().text());
                break;
            case "Last verification error":
                row_tag.children(".last_challenge_error").text($(this).next().text());
                break;
            case "Last delivery error":
                row_tag.children(".last_notification_error").text($(this).next().text());
                break;
            case "Aggregate statistics":
                row_tag.children(".stat").text($(this).next().text());
                break;
            case "Content delivered":
                row_tag.children(".last_notification").text($(this).next().text());
                break;
            default:
                break;
        }
    });
    // last_subscribe_request
    // last_unsubscribe_request
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