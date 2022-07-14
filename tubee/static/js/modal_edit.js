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

document.addEventListener("DOMContentLoaded", (event) => {
  $("#edit-action-modal").on("show.bs.modal", load_edit_modal);
});
