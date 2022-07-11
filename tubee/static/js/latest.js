function mark_all_as_checked(event) {
  const video_ids = $(".video-row")
    .map((index, row) => $(row).data("video-id"))
    .toArray()
    .join(",");
  const api = build_url("api_video.mark_as_checked", {}, { video_ids });

  const button = $(event.target);
  button.toggleButtonLoading();

  $.ajax({ type: "get", url: api })
    .done((responseData) => {
      button.toggleButtonSuccess("Done");
    })
    .fail((responseData) => {
      button.toggleButtonFail(responseData);
    });
}
