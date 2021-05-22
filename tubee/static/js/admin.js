let celery_task_template;

function build_formatted_JSON_tag(data) {
  return $("<pre></pre>").text(JSON.stringify(data, null, 4));
}

function channel_fill_status(responseData) {
  $("#state")
    .empty()
    .append(generate_callback_status_badge(responseData.state));
  $("#expiration").text(responseData.expiration);
  $("#last-notification").text(responseData.last_notification);
  $("#last-notification-error").text(responseData.last_notification_error);
  $("#last-challenge").text(responseData.last_challenge);
  $("#last-challenge-error").text(responseData.last_challenge_error);
  $("#last-subscribe").text(responseData.last_subscribe);
  $("#last-unsubscribe").text(responseData.last_unsubscribe);
  $("#stat").text(responseData.stat);
}

function channel_refresh(event) {
  let button = $(event.target);
  let channel_row = button.parent().parent().parent();
  let status = channel_row.find(".status");
  let expiration = channel_row.find(".expiration");

  button.empty().attr({
    disabled: true,
  });
  status.empty();
  expiration.empty();
  insert_spinner(button, "secondary", true);
  insert_spinner(status, "secondary", true);
  insert_spinner(expiration, "secondary", true);

  $.ajax({
    type: "get",
    url: button.data("endpoint"),
  })
    .done((responseData) => {
      button.empty().text("Refresh").attr({
        disabled: false,
      });
      status.empty().append(generate_callback_status_badge(responseData.state));
      expiration.empty().text(responseData.expiration);
    })
    .fail((responseData) => {
      button.parent().empty().text(responseData);
    });
}

function channel_get_status(event) {
  // Init
  let modal = $(event.target);
  let table = $("#channel-status-table");
  let spinner = $("#channel-status-spinner");

  let endpoint = $(event.relatedTarget).data("endpoint");
  $("#channel-status-modal-title").text($(event.relatedTarget).data("name"));

  spinner.show();
  table.hide();

  $.ajax({
    type: "get",
    url: endpoint,
  })
    .done((responseData) => {
      channel_fill_status(responseData);
      table.show();
    })
    .fail(() => {
      console.log("Failed to load channel status");
      $("#state").text("Error");
      $("#expiration").text("Error");
      $("#last-notification").text("Error");
      $("#last-notification-error").text("Error");
      $("#last-challenge").text("Error");
      $("#last-challenge-error").text("Error");
      $("#last-subscribe").text("Error");
      $("#last-unsubscribe").text("Error");
      $("#stat").text("Error");
    })
    .always(() => {
      spinner.hide();
    });
}

function update_progress(status_url, progress_bar, message_box) {
  // send GET request to status URL
  $.getJSON(status_url)
    .done((data) => {
      // Update UI
      let percent = (data.current / data.total) * 100;
      progress_bar.width(`${percent}%`);
      progress_bar.attr("aria-valuenow", percent);

      // Update after 2 second or terminate
      if (data.status === "Success" || data.status === "Failure") {
        if (data.status === "Success") {
          progress_bar.addClass("bg-success");
        } else {
          progress_bar.width("100%");
          progress_bar.addClass("bg-danger");
        }
        message_box.empty().append(build_formatted_JSON_tag(data.result));
      } else {
        message_box.text(
          `Currently Processing: ${data.result.channel_name} <${data.channel_id}>`
        );
        setTimeout(
          update_progress,
          2000,
          status_url,
          progress_bar,
          message_box
        );
      }
    })
    .fail((data) => {
      progress_bar.width("100%");
      progress_bar.addClass("bg-danger");
      message_box.append(build_formatted_JSON_tag(data));
    });
}

function api_with_progress(event) {
  event.preventDefault();
  // send ajax POST request to start background job
  $.getJSON($(event.target).attr("data-api-endpoint")).done((data) => {
    let progress_bar = $("<div>")
      .attr({
        class: "progress-bar",
        role: "progressbar",
        "aria-valuemin": "0",
        "aria-valuemax": "100",
      })
      .width("0%");
    let message_box = $("<div>");
    $("#management > .results").append(
      $("<div>").addClass("progress my-3").append(progress_bar),
      message_box
    );
    setTimeout(update_progress, 2000, data.status, progress_bar, message_box);
  });
}

function api_get(event) {
  event.preventDefault();
  insert_spinner("#management", "primary");
  $.getJSON($(event.target).attr("data-api-endpoint")).done((data) => {
    $("#management > .results").append(
      $("<pre>").text(JSON.stringify(data, null, 2))
    );
    // console.log(data);
    drop_spinner("#management");
  });
}

function load_tasks(event) {
  insert_spinner("#celery_tasks", "primary");
  let table = $("#celery_tasks > table > tbody");
  table.empty();
  $.getJSON($("#celery-table").attr("data-api-endpoint")).done((data) => {
    data.forEach((element) => {
      let row = $(celery_task_template).clone();
      row
        .find(".task-name")
        .text(`${element.request.name}\n${element.request.id}`);
      row
        .find(".task-args")
        .text(JSON.stringify(element.request.args, null, 2));
      row.find(".task-eta").text(moment(element.eta).fromNow());
      if (element.active) {
        row
          .find(".task-active")
          .empty()
          .append($("<span>").addClass("badge badge-success").text("Active"));
      } else {
        row
          .find(".task-active")
          .empty()
          .append($("<span>").addClass("badge badge-danger").text("Revoked"));
      }
      table.append(row);
    });
    drop_spinner("#celery_tasks");
  });
}

$(document).ready(() => {
  $("#btn-refresh-all").click(() => {
    $(".btn-refresh").click();
  });
  $(".btn-refresh").click(channel_refresh);
  $("#channel-status-modal").on("show.bs.modal", channel_get_status);
  $("#channel-renew-all").click(api_with_progress);
  $("#channel-renew-all-schedule").click(api_get);
  $("#channel-renew-all-random").click(api_get);
  $("#task-remove-all").click(api_get);
  $("#management-tab").on("shown.bs.tab", (event) => {
    $("#management > .results").empty();
  });
  $("#celery_tasks-tab").on("shown.bs.tab", load_tasks);
  $.ajax($("#celery-table").attr("data-template-endpoint")).done((data) => {
    celery_task_template = $.parseHTML(data);
  });
});
