function unsubscribe(event) {
  let unsubscribe_btn = $(event.target);
  let loaded_div = $("<div>").load(
    "static/component/channel_unsubscribe.html",
    function () {
      let channel_name = unsubscribe_btn.data("channel-name");
      let api_endpoint = unsubscribe_btn.data("api-endpoint");
      $(".modal-body").text(
        `Are you sure you want to unsubscribe to ${channel_name}?`
      );
      $("#unsubscribe-modal")
        .modal("show")
        .on("hidden.bs.modal", function (event) {
          loaded_div.remove();
        });
      $("#confirm-btn").on("click", function () {
        $.get(api_endpoint).done(function (data) {
          if (Boolean(data)) {
            location.reload();
          } else {
            alert("Unsubscribe Failed, Try Again");
          }
        });
      });
    }
  );
  $("#content-container").append(loaded_div);
}

$(document).ready(() => {
  $(".unsubscribe-btn").on("click", unsubscribe);
});
