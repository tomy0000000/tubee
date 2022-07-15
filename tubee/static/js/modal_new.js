function send_new_action_request(event) {
  // Init
  event.preventDefault();
  const button = $(event.target);
  const url = buildURL("api_action.new");
  const data = $("#new-action-form").serializeArray();

  // Appearance
  set_loading(button);

  // Request
  $.post({ url, data })
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

document.addEventListener("DOMContentLoaded", (event) => {
  $("#new-action-modal").on("show.bs.modal", load_new_modal);
});
