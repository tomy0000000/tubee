function update_progress(status_url, progress_bar, message_box) {
  // send GET request to status URL
  $.getJSON(status_url).done((data) => {
    // Update UI
    let percent = (data.current / data.total) * 100;
    progress_bar.width(`${percent}%`);
    progress_bar.attr("aria-valuenow", percent);

    // Update after 2 second or terminate
    if (data.status === "Success" || data.status === "Failure") {
      if (data.status === "Success") {
        progress_bar.addClass("bg-success");
      } else {
        progress_bar.addClass("bg-danger");
      }
      message_box.text(JSON.stringify(data.result));
    } else {
      message_box.text(`Currently Processing: ${data.channel_id}`);
      setTimeout(() => {
        update_progress(status_url, progress_bar, message_box);
      }, 2000);
    }
  });
}

$(document).ready(function () {
  $(".channel-renew-api-btn").click(function (element) {
    element.preventDefault();
    // send ajax POST request to start background job
    $.getJSON($(this).attr("data-api-endpoint")).done((data) => {
      let progress_bar = $("<div>")
        .attr({
          class: "progress-bar",
          role: "progressbar",
          "aria-valuemin": "0",
          "aria-valuemax": "100",
        })
        .width("0%");
      let message_box = $("<div>");
      $("#management").append(
        $("<div>").addClass("progress my-3").append(progress_bar),
        message_box
      );
      update_progress(data.status, progress_bar, message_box);
    });
  });
});
