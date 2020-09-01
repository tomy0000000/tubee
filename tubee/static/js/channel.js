let edit_modal = $("#edit-action-modal");

let reload_hub_status = (event) => {
    event.preventDefault();
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

let load_new_modal = (event) => {
    // Init
    let modal = $(event.target);
    let submit_button = modal.find(".submit-btn");
    let action_type_input = modal.find("#action_type");

    // Appearence
    $(".new-action-save-spinner").hide();
    submit_button.prop("disabled", false);

    // Bind event
    refresh_action_fields(action_type_input.val());
    action_type_input.change((event) => {
        event.preventDefault();
        refresh_action_fields($(event.target).val());
    });
    submit_button.click(send_new_action_request);
};

let load_edit_modal = (event) => {
    // Init
    let submit_button = edit_modal.find(".submit-btn");
    let action_type_input = edit_modal.find("#action_type");
    let api_endpoint = $(event.relatedTarget).data("api-endpoint");
    submit_button.data("api-endpoint", api_endpoint);

    // Appearence
    $("#edit-loading-spinner").show();
    $("#edit-action-form").hide();
    $("#edit-save-spinner").hide();
    submit_button.prop("disabled", false);

    // TODO: Edit API is not enabled yet
    submit_button.prop("disabled", true);

    // Load Action Info
    $.get(api_endpoint)
        .done(load_action_context)
        .fail(() => {
            alert("Oops, Something went wrong");
            location.reload();
        });

    // Bind event
    refresh_action_fields(action_type_input.val());
    action_type_input.change((event) => {
        event.preventDefault();
        refresh_action_fields($(event.target).val());
    });
    submit_button.click(send_edit_action_request);
};

let load_remove_modal = (event) => {
    // Init
    let modal = $(event.target);
    let submit_button = modal.find(".submit-btn");
    let api_endpoint = $(event.relatedTarget).data("api-endpoint");
    let action_name = $(event.relatedTarget).data("action-name");
    submit_button.data("api-endpoint", api_endpoint);

    // Appearence
    modal.find(".remove-action-save-spinner").hide();
    submit_button.prop("disabled", false);
    modal
        .find(".modal-body")
        .text(`Are you sure you want to remove action ${action_name}?`);

    // Bind event
    submit_button.click(send_delete_action_request);
};

let send_new_action_request = (event) => {
    // Init
    event.preventDefault();
    let button = $(event.target);
    let api_endpoint = button.data("api-endpoint");
    let data = $("#new-action-form").serializeArray();

    // Appearence
    $(".new-action-save-spinner").show();
    button.prop("disabled", true);

    // Request
    $.post(api_endpoint, data, (requestData) => {
        console.log(requestData);
    })
        .done((responseData) => {
            if (Boolean(responseData)) {
                $("#new-action-modal").modal("hide");
                location.reload();
            } else {
                alert("Save Failed, Try Again");
                $(".new-action-save-spinner").hide();
                button.prop("disabled", false);
            }
        })
        .fail(() => {
            alert("Save Failed, Try Again");
            $(".new-action-save-spinner").hide();
            button.prop("disabled", false);
        })
        .always((responseData) => {
            console.log(responseData);
        });
};

let send_edit_action_request = (event) => {
    // Init
    event.preventDefault();
    let button = $(event.target);
    let api_endpoint = button.data("api-endpoint");
    let data = $("#edit-action-form").serializeArray();

    // Appearence
    $("#edit-save-spinner").show();
    button.prop("disabled", true);

    // Request
    $.post(api_endpoint, data, (requestData) => {
        console.log(requestData);
    })
        .done((responseData) => {
            console.log(Boolean(responseData));
            if (Boolean(responseData)) {
                $("#edit-action-modal").modal("hide");
                location.reload();
            } else {
                alert("Save Failed, Try Again");
                $("#edit-save-spinner").hide();
                button.prop("disabled", false);
            }
        })
        .fail((responseData) => {
            alert("Save Failed, Try Again");
            $("#edit-save-spinner").hide();
            button.prop("disabled", false);
        });
};

let send_delete_action_request = (event) => {
    // Init
    event.preventDefault();
    let button = $(event.target);
    let api_endpoint = button.data("api-endpoint");

    // Appearence
    $(".remove-action-save-spinner").show();
    button.prop("disabled", true);

    // Request
    $.ajax(api_endpoint, {
        method: "DELETE",
    })
        .done((responseData) => {
            if (Boolean(responseData)) {
                $("#remove-action-modal").modal("hide");
                location.reload();
            } else {
                alert("Remove Failed, Try Again");
                $(".remove-action-save-spinner").hide();
                button.prop("disabled", false);
            }
        })
        .fail(() => {
            alert("Remove Failed, Try Again");
            $(".remove-action-save-spinner").hide();
            button.prop("disabled", false);
        })
        .always((responseData) => {
            console.log(responseData);
        });
};

let load_action_context = (data) => {
    edit_modal.find("#action_name").val(data.action_name);
    edit_modal
        .find("#action_type")
        .val(data.action_type)
        .prop("disabled", true);
    refresh_action_fields(data.action_type);
    switch (data.action_type) {
        case "Notification":
            edit_modal.find("#notification-service").val(data.details.service);
            edit_modal.find("#notification-message").val(data.details.message);
            edit_modal.find("#notification-title").val(data.details.title);
            edit_modal.find("#notification-url").val(data.details.url);
            edit_modal
                .find("#notification-url_title")
                .val(data.details.url_title);
            edit_modal
                .find("#notification-image_url")
                .val(data.details.image_url);
            break;
        case "Playlist":
            edit_modal
                .find("#playlist-playlist_id")
                .val(data.details.playlist_id);
            break;
        case "Download":
            edit_modal.find("#download-file_path").val(data.details.file_path);
            break;
        default:
            break;
    }
    $("#edit-loading-spinner").hide();
    $("#edit-action-form").show();
};

let refresh_action_fields = (type) => {
    $(".action-type-fields").hide();
    if (type === "Notification") {
        $(".notification-fields").show();
    } else if (type === "Playlist") {
        $(".playlist-fields").show();
    } else if (type === "Download") {
        $(".download-fields").show();
    } else {
        console.log("Unknown Type");
    }
};

$(document).ready(function () {
    $("#hub-reload-btn").click(reload_hub_status);
    $("#new-action-modal").on("show.bs.modal", load_new_modal);
    $("#edit-action-modal").on("show.bs.modal", load_edit_modal);
    $("#remove-action-modal").on("show.bs.modal", load_remove_modal);
});
