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

document.addEventListener("DOMContentLoaded", (event) => {
  $("#remove-action-modal").on("show.bs.modal", load_remove_modal);
});
