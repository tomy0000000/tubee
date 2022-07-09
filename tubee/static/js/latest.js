function mark_all_as_checked(event) {
  const button = $(event.target);

  button.empty().attr({ disabled: true });
  insert_spinner(".all-checked-btn", "secondary", true);

  const video_ids = $(".video-row")
    .map((index, row) => $(row).data("video-id"))
    .toArray()
    .join(",");
  const api = build_url("api_video.mark_as_checked", {}, { video_ids });
  console.log(api);

  $.ajax({ type: "get", url: api })
    .done((responseData) => {
      button.empty().text("Done");
    })
    .fail((responseData) => {
      button.parent().empty().text(responseData);
    })
    .always(() => {
      drop_spinner(".all-checked-btn");
    });
}

$(document).ready(function () {
  $(".all-checked-btn").click(mark_all_as_checked);
});
