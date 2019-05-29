$(document).ready(function() {
    $("#loading-spinner").hide();
    $("#subscription-table").one("load-more", load_more);
});

$(window).scroll(function() {
    var trigger_loading_row = $("#subscription-table tr:eq(-10)");
    var hT = trigger_loading_row.offset().top,
        hH = trigger_loading_row.outerHeight(),
        wH = $(window).height(),
        wS = $(this).scrollTop();
    if (wS > (hT + hH - wH)) {
        $("#subscription-table").trigger("load-more");
    }
});

function build_row(channel) {
    var row = $("#subscription-table tr:eq(1)").clone();
    row.find(".channel-thumbnails").attr("src", channel.snippet.thumbnails.medium.url);
    row.find(".channel-name").text(channel.snippet.title);
    row.find(".channel-id-a").attr("data-clipboard-text", channel.snippet.channelId);
    row.find(".channel-id-p").text(channel.snippet.channelId);
    row.find(".channel-subscribed").empty();
    if (!channel.snippet.subscribed) {
        $("<a>", {
            "class": "btn btn-success",
            "href": channel.snippet.subscribe_endpoint,
            "role": "button"
        }).text("Subscribe").appendTo(row.find(".channel-subscribed"));
    }
    return row
}

function load_more() {
    $("#loading-spinner").show();
    console.log("Trigger Loading");
    var api_endpoint = $("#subscription-table").attr("data-api-endpoint");
    var page_token = $("#subscription-table").attr("data-next-page-token");
    $.getJSON(api_endpoint, {
        "page_token": page_token
    }).done(function(response_data) {
        response_data.items.forEach(function(channel){
            build_row(channel).appendTo("#subscription-table tbody");
        })
        if ("nextPageToken" in response_data) {
            $("#subscription-table").attr("data-next-page-token", response_data.nextPageToken);
            $("#subscription-table").one("load-more", load_more);
        }
    }).fail(function(response_data) {
        console.log("Oops! Something Went Wrong...");
    }).always(function(response_data) {
        console.log("Request Sent");
        $("#loading-spinner").hide();
    });
}