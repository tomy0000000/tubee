function send_tag_patch(event) {
  // Init
  event.preventDefault();
  let button = $(event.target);
  let api_endpoint = button.data("api-endpoint");
  let data = $("#tag-form").serializeArray();

  // Appearance
  button.append(
    $(
      '<span class="spinner-border spinner-border-sm spinner" role="status" aria-hidden="true"></span>'
    )
  );
  button.prop("disabled", true);

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
        location.reload();
      } else {
        alert("Save Failed, Try Again");
      }
    })
    .fail(() => {
      alert("Save Failed, Try Again");
    })
    .always((responseData) => {
      console.log(responseData);
      button.find(".spinner").remove();
      button.prop("disabled", false);
    });
}

$(document).ready(function () {
  $("#tag-form").find(".submit-btn").click(send_tag_patch);
});
