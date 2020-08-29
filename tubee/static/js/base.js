insert_spinner = (location, type) => {
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
