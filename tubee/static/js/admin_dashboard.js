function update_progress(status_url) {
  // send GET request to status URL
  $.getJSON(status_url).done((data) => {
    // Update UI
    let percent = (data.current / data.total) * 100;
    $("#progressbar").width(`${percent}%`);
    $("#progressbar").attr("aria-valuenow", percent);
    $("#channel-renew-results").text(
      `Currently Processing: ${data.channel_id}`
    );
    // Update after 2 second or terminate
    if (data.status === "Success" || data.status === "Failure") {
      if (data.status === "Success") {
        $("#progressbar").addClass("bg-success");
      } else {
        $("#progressbar").addClass("bg-danger");
      }
      $("#channel-renew").append(
        $("#channel-renew-results").text(JSON.stringify(data.result))
      );
    } else {
      setTimeout(() => {
        update_progress(status_url);
      }, 2000);
    }
  });
}

$(document).ready(function () {
  $("#start-renew-btn").click(function (e) {
    e.preventDefault();
    // send ajax POST request to start background job
    $.getJSON($(this).attr("data-api-endpoint")).done((data) => {
      $("#channel-renew").append(
        $("<div>")
          .addClass("progress my-3")
          .append(
            $("<div>")
              .attr({
                id: "progressbar",
                class: "progress-bar",
                role: "progressbar",
                "aria-valuemin": "0",
                "aria-valuemax": "100",
              })
              .width("0%")
          ),
        $("<div>").attr("id", "channel-renew-results")
      );
      update_progress(data.status);
    });
  });
});
