const VALID_SPINNER_TYPE = [
    "primary",
    "secondary",
    "success",
    "danger",
    "warning",
    "info",
    "light",
    "dark",
];

insert_spinner = (location, type) => {
    type = VALID_SPINNER_TYPE.includes(type) ? type : "primary";
    $(location).append(
        $("<div>")
            .attr({
                id: "loading-spinner-div",
                class: ["d-flex", "justify-content-center"],
            })
            .append(
                $("<div>")
                    .addClass(["spinner-border", `text-${type}`])
                    .append($("<span>").addClass("sr-only").text("Loading..."))
            )
    );
};

drop_spinner = (location) => {
    $(location).find("#loading-spinner-div").remove();
};

register_clipboard_items = (selector) => {
    let clipboard = new ClipboardJS(selector);
    clipboard.on("success", (event) => {
        $(event.trigger)
            .tooltip({
                placement: "right",
                title: "Copied!",
                trigger: "manual",
            })
            .tooltip("show")
            .mouseleave((event) => {
                $(event.currentTarget).tooltip("hide");
            });
    });
};

submit_subscribe = (event) => {
    // UI
    let icon = $("<span>").attr({
        class: "spinner-border spinner-border-sm mr-1",
        role: "status",
        "aria-hidden": true,
    });
    let text = $("<span>").addClass("aria-hidden").text("Loading...");
    $(event.currentTarget).prop("disabled", true).empty().append(icon, text);

    // API
    let is_navbar =
        $(event.currentTarget).attr("id") === "navbar-subscribe-submit"; // false for youtube subscription
    let api_endpoint = $("#navbar-subscribe-submit").data("subscribe-api");
    let channel_id = is_navbar
        ? $("#subscribe-input").val()
        : $(event.currentTarget).data("channel-id");
    api_endpoint = api_endpoint.replace(encodeURI("<channel_id>"), channel_id);
    $.ajax({
        type: "GET",
        url: api_endpoint,
        success: (response) => {
            if (response) {
                if (is_navbar) {
                    location.href = $("#navbar-main").attr("href");
                } else {
                    icon.remove();
                    $(event.currentTarget).prepend(
                        $("<i>").addClass("fas fa-check mr-1")
                    );
                    text.text("Done!");
                    console.log(response);
                }
            } else {
                alert("Something went wrong");
                if (is_navbar) {
                    location.reload();
                } else {
                    $(event.currentTarget)
                        .removeClass("btn-success")
                        .addClass("btn-danger");
                    icon.remove();
                    $(event.currentTarget).prepend(
                        $("<i>").addClass("fas fa-times mr-1")
                    );
                    text.text("Error");
                    console.log(response);
                }
            }
        },
    });
};

$(document).ready(() => {
    register_clipboard_items(".clipboard");
    $(".subscribe-submit").click(submit_subscribe);

    let channel_search_api = $("#subscribe-input").data("channel-api");
    $("#subscribe-input").autoComplete({
        resolverSettings: {
            url: channel_search_api,
            queryKey: "query",
            requestThrottling: 1000,
        },
        formatResult: (item) => {
            return {
                value: item.id,
                text: item.id,
                html: [
                    $("<div>")
                        .addClass("d-flex align-items-center")
                        .append(
                            $("<div>").append(
                                $("<img>")
                                    .attr({
                                        class: "rounded-circle",
                                        src: item.thumbnail,
                                    })
                                    .css("height", "2rem")
                            ),
                            $("<div>").append(
                                $("<p>").addClass("mb-0 ml-2").text(item.title)
                            )
                        ),
                ],
            };
        },
    });
});
