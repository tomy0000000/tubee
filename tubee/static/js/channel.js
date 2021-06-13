function reload_hub_status(event) {
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
        state in BADGE_TYPE_MAPPING ? BADGE_TYPE_MAPPING[state] : "info";
      let badge = $("<span></span>")
        .addClass(`badge bg-${badge_type}`)
        .text(state);
      $("#state").empty().append(badge);

      $("#expiration").text(responseData.expiration);
      $("#last-notification").text(responseData.last_notification);
      $("#last-notification-error").text(responseData.last_notification_error);
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
}

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
  $("#hub-reload-btn").click(reload_hub_status);
});
