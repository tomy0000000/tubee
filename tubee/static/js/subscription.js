function unsubscribe(event) {
  let unsubscribe_btn = $(event.target);
  let loaded_div = $("<div>").load(
    "static/component/channel_unsubscribe.html",
    () => {
      const channel_id = unsubscribe_btn.data("channel-id");
      const channel_name = unsubscribe_btn.data("channel-name");
      const api_endpoint = unsubscribe_btn.data("api-endpoint");
      $(".modal-body").text(
        `Are you sure you want to unsubscribe to ${channel_name}?`
      );
      $("#unsubscribe-modal")
        .modal("show")
        .on("hidden.bs.modal", () => {
          loaded_div.remove();
        });
      $("#confirm-btn").on("click", async function () {
        let form = document.getElementById(`${channel_id}-unsubscribe-form`);
        await fetch_post_form(api_endpoint, form);
        location.reload();
      });
    }
  );
  $("#content-container").append(loaded_div);
}

$(document).ready(() => {
  $(".unsubscribe-btn").on("click", unsubscribe);
});
