let celery_task_template;
update_progress = (status_url, progress_bar, message_box) => {
    // send GET request to status URL
    $.getJSON(status_url).done((data) => {
        // Update UI
        let percent = (data.current / data.total) * 100;
        progress_bar.width(`${percent}%`);
        progress_bar.attr("aria-valuenow", percent);

        // Update after 2 second or terminate
        if (data.status === "Success" || data.status === "Failure") {
            if (data.status === "Success") {
                progress_bar.addClass("bg-success");
            } else {
                progress_bar.addClass("bg-danger");
            }
            message_box.text(JSON.stringify(data.result));
        } else {
            message_box.text(`Currently Processing: ${data.channel_id}`);
            setTimeout(
                update_progress,
                2000,
                status_url,
                progress_bar,
                message_box
            );
        }
    });
};

api_with_progress = (event) => {
    event.preventDefault();
    // send ajax POST request to start background job
    $.getJSON($(event.target).attr("data-api-endpoint")).done((data) => {
        let progress_bar = $("<div>")
            .attr({
                class: "progress-bar",
                role: "progressbar",
                "aria-valuemin": "0",
                "aria-valuemax": "100",
            })
            .width("0%");
        let message_box = $("<div>");
        $("#management > .results").append(
            $("<div>").addClass("progress my-3").append(progress_bar),
            message_box
        );
        setTimeout(
            update_progress,
            2000,
            data.status,
            progress_bar,
            message_box
        );
    });
};

api_get = (event) => {
    event.preventDefault();
    insert_spinner("#management", "primary");
    $.getJSON($(event.target).attr("data-api-endpoint")).done((data) => {
        $("#management > .results").append(
            $("<pre>").text(JSON.stringify(data, null, 2))
        );
        // console.log(data);
        drop_spinner("#management");
    });
};

load_tasks = (event) => {
    insert_spinner("#celery-tasks", "primary");
    let table = $("#celery-tasks > table > tbody");
    table.empty();
    $.getJSON($("#celery-table").attr("data-api-endpoint")).done((data) => {
        data.forEach((element) => {
            let row = $(celery_task_template).clone();
            row.find(".task-name").text(
                `${element.request.name}\n${element.request.id}`
            );
            row.find(".task-args").text(
                JSON.stringify(element.request.args, null, 2)
            );
            row.find(".task-eta").text(moment(element.eta).fromNow());
            if (element.active) {
                row.find(".task-active")
                    .empty()
                    .append(
                        $("<span>")
                            .addClass("badge badge-success")
                            .text("Active")
                    );
            } else {
                row.find(".task-active")
                    .empty()
                    .append(
                        $("<span>")
                            .addClass("badge badge-danger")
                            .text("Revoked")
                    );
            }
            table.append(row);
        });
        drop_spinner("#celery-tasks");
    });
};

$(document).ready(() => {
    $("#channel-renew-all").click(api_with_progress);
    $("#channel-renew-all-schedule").click(api_get);
    $("#task-remove-all").click(api_get);
    $("#management-tab").on("shown.bs.tab", (event) => {
        $("#management > .results").empty();
    });
    $("#celery-tasks-tab").on("shown.bs.tab", load_tasks);
    $.ajax($("#celery-table").attr("data-template-endpoint")).done((data) => {
        celery_task_template = $.parseHTML(data);
    });
});
