load_edit_modal = (action_operation) => {
    $("#edit_save_spinner").hide();
    $("#edit_action_modal").find("#submit").prop("disabled", false);
    let api_endpoint;

    if (action_operation === "new") {
        $("#edit_action_modal").find(".modal-title").text("New Action");
        api_endpoint = "/api/action/new";
        $("#action_type").prop("disabled", false);
        $("#edit_loading_spinner").hide();
    } else {
        $("#edit_action_modal").find(".modal-title").text("Edit Action");
        api_endpoint = "/api/action/edit";
        $("#edit_loading_spinner").show();
        $("#action_form").hide();
        $.get(`/api/${action_operation}`).done(function (data) {
            $("#action_name").val(data.action_name);
            $("#action_type").val(data.action_type).prop("disabled", true);
            $("#edit_loading_spinner").hide();
            $("#action_form").show();
        });
    }
    refresh_action_fields($("#action_type").val());
    return api_endpoint;
};

load_remove_modal = (action_name) => {
    // Appearence
    $("#remove_spinner").hide();
    $("#remove_button").prop("disabled", false);
    $("#remove_action_modal")
        .find(".modal-body")
        .text(`Are you sure you want to remove action ${action_name}?`);
};

refresh_action_fields = (type) => {
    $(".action-type-fields").hide();
    if (type === "Notification") {
        $("#notification-fields").show();
    } else if (type === "Playlist") {
        $("#playlist-fields").show();
    } else if (type === "Download") {
        $("#download-fields").show();
    } else {
        console.log("Unknown Type");
    }
};

reload_hub_status = () => {
    insert_spinner($("#state"), "primary");
    insert_spinner($("#expiration"), "danger");
    insert_spinner($("#last-notification"), "success");
    insert_spinner($("#last-notification-error"), "warning");
    insert_spinner($("#last-challenge"), "success");
    insert_spinner($("#last-challenge-error"), "warning");
    insert_spinner($("#last-subscribe"), "info");
    insert_spinner($("#last-unsubscribe"), "info");
    insert_spinner($("#stat"), "dark");

    // Start Request
    $.ajax({
        type: "get",
        url: $("#status-grid").data("api-endpoint"),
    })
        .done((responseData) => {
            let state = responseData.state;
            const BADGE_TYPE_MAPPING = {
                verified: "success",
                expired: "danger",
                unverified: "warning",
                unsubscribed: "secondary",
            };
            let badge_type =
                state in BADGE_TYPE_MAPPING
                    ? BADGE_TYPE_MAPPING[state]
                    : "info";
            let badge = $("<span></span>")
                .addClass(`badge badge-${badge_type}`)
                .text(state);
            $("#state").empty().append(badge);

            $("#expiration").text(responseData.expiration);
            $("#last-notification").text(responseData.last_notification);
            $("#last-notification-error").text(
                responseData.last_notification_error
            );
            $("#last-challenge").text(responseData.last_challenge);
            $("#last-challenge-error").text(responseData.last_challenge_error);
            $("#last-subscribe").text(responseData.last_subscribe);
            $("#last-unsubscribe").text(responseData.last_unsubscribe);
            $("#stat").text(responseData.stat);
        })
        .fail(function (responseData) {
            console.log("Hub Status Request Failed");
            $("#state").text("Error");
            $("#expiration").text("Error");
            $("#last-notification").text("Error");
            $("#last-notification-error").text("Error");
            $("#last-challenge").text("Error");
            $("#last-challenge-error").text("Error");
            $("#last-subscribe").text("Error");
            $("#last-unsubscribe").text("Error");
            $("#stat").text("Error");
        });
};

$(document).ready(function () {
    $("#hub-reload-btn").click(function (event) {
        event.preventDefault();
        reload_hub_status();
    });

    // Edit Action Modals
    $("#edit_action_modal").on("show.bs.modal", function (event) {
        let button = $(event.relatedTarget); // Button that triggered the modal
        let action_id = button.data("action-id"); // Extract info from data-* attributes
        let api_endpoint = load_edit_modal(action_id);

        $(this)
            .find("#action_type")
            .on("change", function (event) {
                event.preventDefault();
                refresh_action_fields($(this).val());
            });

        $(this)
            .find("#submit")
            .on("click", function (event) {
                // Appearence
                event.preventDefault();
                $("#edit_save_spinner").show();
                $(this).prop("disabled", true);
                $("#action_form").serializeArray();
                // Request
                $.post(
                    api_endpoint,
                    $("#action_form").serializeArray(),
                    function (data, textStatus, xhr) {
                        console.log(data);
                    }
                )
                    .done(function (responseData) {
                        console.log(Boolean(responseData));
                        if (Boolean(responseData)) {
                            $("#edit_action_modal").modal("hide");
                            location.reload();
                        } else {
                            alert("Save Failed, Try Again");
                            load_edit_modal(action_id);
                        }
                    })
                    .fail(function (responseData) {
                        alert("Save Failed, Try Again");
                        load_edit_modal(action_id);
                    });
            });
    });

    // Remove Action Modals
    $("#remove_action_modal").on("show.bs.modal", function (event) {
        let button = $(event.relatedTarget);
        let action_id = button.data("action-id");
        let action_name = button.data("action-name");
        load_remove_modal(action_name);
        $("#remove_button").on("click", function (event) {
            // Appearence
            event.preventDefault();
            $("#remove_spinner").show();
            $(this).prop("disabled", true);
            // Request
            $.get(`/api/${action_id}/remove`)
                .done(function (data) {
                    console.log(Boolean(data));
                    if (Boolean(data)) {
                        $("#remove_action_modal").modal("hide");
                        location.reload();
                    } else {
                        alert("Remove Failed, Try Again");
                    }
                })
                .fail(function (responseData) {
                    alert("Remove Failed, Try Again");
                    load_remove_modal(action_name);
                });
        });
    });
});
