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
});
