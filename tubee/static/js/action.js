function refresh_action_fields(type) {
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
}

function load_action_context(data) {
  $("#edit-action-modal").find("#action_name").val(data.action_name);
  $("#edit-action-modal").find("#action_type").val(data.action_type);
  refresh_action_fields(data.action_type);
  switch (data.action_type) {
    case "Notification":
      $("#edit-action-modal")
        .find("#notification-service")
        .val(data.details.service);
      $("#edit-action-modal")
        .find("#notification-message")
        .val(data.details.message);
      $("#edit-action-modal")
        .find("#notification-title")
        .val(data.details.title);
      $("#edit-action-modal").find("#notification-url").val(data.details.url);
      $("#edit-action-modal")
        .find("#notification-url_title")
        .val(data.details.url_title);
      $("#edit-action-modal")
        .find("#notification-image_url")
        .val(data.details.image_url);
      break;
    case "Playlist":
      $("#edit-action-modal")
        .find("#playlist-playlist_id")
        .val(data.details.playlist_id);
      break;
    case "Download":
      $("#edit-action-modal")
        .find("#download-file_path")
        .val(data.details.file_path);
      break;
    default:
      break;
  }
  $("#edit-loading-spinner").hide();
  $("#edit-action-form").show();
}

function load_new_modal(event) {
  // Init
  let modal = $(event.target);
  let button = modal.find(".submit-btn");
  let action_type_input = modal.find("#action_type");

  // Appearance
  unset_loading(button);

  // Bind event
  refresh_action_fields(action_type_input.val());
  action_type_input.change((event) => {
    event.preventDefault();
    refresh_action_fields($(event.target).val());
  });
  button.click(send_new_action_request);
}

function load_edit_modal(event) {
  // Init
  let button = $("#edit-action-modal").find(".submit-btn");
  let action_type_input = $("#edit-action-modal").find("#action_type");
  let read_endpoint = $(event.relatedTarget).data("read-endpoint");
  let edit_endpoint = $(event.relatedTarget).data("edit-endpoint");
  button.data("edit-endpoint", edit_endpoint);

  // Appearance
  $("#edit-loading-spinner").show();
  $("#edit-action-form").hide();
  unset_loading(button);

  // Load Action Info
  $.get(read_endpoint)
    .done(load_action_context)
    .fail(() => {
      alert("Oops, Something went wrong");
      location.reload();
    });

  // Bind event
  action_type_input.change((event) => {
    event.preventDefault();
    refresh_action_fields($(event.target).val());
  });
  button.click(send_edit_action_request);
}

function load_remove_modal(event) {
  // Init
  let modal = $(event.target);
  let submit_button = modal.find(".submit-btn");
  let api_endpoint = $(event.relatedTarget).data("api-endpoint");
  let action_name = $(event.relatedTarget).data("action-name");
  submit_button.data("api-endpoint", api_endpoint);

  // Appearance
  modal.find(".remove-action-save-spinner").hide();
  submit_button.prop("disabled", false);
  modal
    .find(".modal-body")
    .text(`Are you sure you want to remove action ${action_name}?`);

  // Bind event
  submit_button.click(send_delete_action_request);
}

function send_new_action_request(event) {
  // Init
  event.preventDefault();
  let button = $(event.target);
  let api_endpoint = button.data("api-endpoint");
  let data = $("#new-action-form").serializeArray();

  // Appearance
  set_loading(button);

  // Request
  $.post({
    type: "POST",
    url: api_endpoint,
    data: data,
    success: (requestData) => {
      console.log(requestData);
    },
  })
    .done((responseData) => {
      if (Boolean(responseData)) {
        $("#new-action-modal").modal("hide");
        location.reload();
      } else {
        alert("Save Failed, Try Again");
        unset_loading(button);
      }
    })
    .fail(() => {
      alert("Save Failed, Try Again");
      unset_loading(button);
    })
    .always((responseData) => {
      console.log(responseData);
    });
}

function send_edit_action_request(event) {
  // Init
  event.preventDefault();
  let button = $(event.target);
  let edit_endpoint = button.data("edit-endpoint");
  let data = $("#edit-action-form").serializeArray();

  // Appearance
  set_loading(button);

  // Request
  $.post({
    type: "PATCH",
    url: edit_endpoint,
    data: data,
    success: (requestData) => {
      console.log(requestData);
    },
  })
    .done((responseData) => {
      console.log(Boolean(responseData));
      if (Boolean(responseData)) {
        $("#edit-action-modal").modal("hide");
        location.reload();
      } else {
        alert("Save Failed, Try Again");
        unset_loading(button);
      }
    })
    .fail((responseData) => {
      alert("Save Failed, Try Again");
      unset_loading(button);
    });
}

function send_delete_action_request(event) {
  // Init
  event.preventDefault();
  let button = $(event.target);
  let api_endpoint = button.data("api-endpoint");

  // Appearance
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
}

$(document).ready(function () {
  $("#new-action-modal").on("show.bs.modal", load_new_modal);
  $("#edit-action-modal").on("show.bs.modal", load_edit_modal);
  $("#remove-action-modal").on("show.bs.modal", load_remove_modal);
});
