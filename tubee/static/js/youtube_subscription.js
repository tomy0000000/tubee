var row_template;

$(document).ready(() => {
    // Load row template
    let template_endpoint = $("#subscription-table").attr(
        "data-channel-row-endpoint"
    );
    $.ajax(template_endpoint).done((raw_text) => {
        row_template = $.parseHTML(raw_text);
        load_more();
    });
    $("#subscription-table").one("load-more", load_more);
});

$(window).scroll(() => {
    console.log("scroll Event Captured");
    let trigger_loading_row = $("#subscription-table tr:eq(-10)");
    let hT = trigger_loading_row.offset().top,
        hH = trigger_loading_row.outerHeight(),
        wH = $(window).height(),
        wS = $(this).scrollTop();
    if (wS > hT + hH - wH) {
        $("#subscription-table").trigger("load-more");
    }
});

build_row = (channel) => {
    let row = $(row_template).clone();
    row.find(".channel-thumbnails").attr(
        "src",
        channel.snippet.thumbnails.medium.url
    );
    row.find(".channel-name").text(channel.snippet.title);
    row.find(".channel-id-a").attr(
        "data-clipboard-text",
        channel.snippet.channelId
    );
    row.find(".channel-id-p").text(channel.snippet.channelId);
    if (!channel.snippet.subscribed) {
        row.find(".channel-subscribed").append(
            $("<button>", {
                class: "btn btn-success subscribe-submit",
                type: "button",
                "data-channel-id": channel.snippet.channelId,
            })
                .text("Subscribe")
                .appendTo(row.find(".channel-subscribed"))
        );
    }
    return row;
};

load_more = () => {
    $("#loading-spinner").show();
    let api_endpoint = $("#subscription-table").attr("data-api-endpoint");
    let page_token = $("#subscription-table").attr("data-next-page-token");
    $.getJSON(api_endpoint, {
        page_token: page_token,
    })
        .done((response_data) => {
            // Build row for each channel
            response_data.items.forEach((channel) => {
                $("#subscription-table tbody").append(build_row(channel));
                // build_row(channel).appendTo("#subscription-table tbody");
            });
            $(".subscribe-submit").click(submit_subscribe);

            // Store nextPageToken to table
            if ("nextPageToken" in response_data) {
                $("#subscription-table").attr(
                    "data-next-page-token",
                    response_data.nextPageToken
                );
                $("#subscription-table").one("load-more", load_more);
            }

            // Initialize Clipboard JS
            new ClipboardJS(".clipboard");
            $(".clipboard")
                .tooltip({
                    placement: "right",
                    title: "Copied!",
                    trigger: "click",
                })
                .on("mouseleave", function () {
                    $(this).tooltip("hide");
                })
                .on("click", (event) => {
                    event.preventDefault();
                });
        })
        .fail((response_data) => {
            console.log("Oops! Something Went Wrong...");
        })
        .always((response_data) => {
            console.log("Request Sent");
            $("#loading-spinner").hide();
        });
};
