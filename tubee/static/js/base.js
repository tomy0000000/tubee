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

$(document).ready(() => {
    new ClipboardJS(".clipboard");
    $(".clipboard")
        .tooltip({
            placement: "right",
            title: "Copied!",
            trigger: "click",
        })
        .on("mouseleave", (element) => {
            $(element).tooltip("hide");
        })
        .on("click", (event) => {
            event.preventDefault();
        });
    $("#subscribe-input").autoComplete({
        resolver: "custom",
        events: {
            search: function (query, callback, element) {
                let url = $(element).data("channel-api");
                console.log(url);
                $.ajax(url, {
                    data: { query: query },
                }).done(function (result) {
                    console.log(result);
                    callback(result);
                });
            },
        },
        formatResult: function (item) {
            return {
                value: item.id,
                text: item.title,
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
        resolverSettings: {
            requestThrottling: 1000,
        },
    });
});
