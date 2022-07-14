//
// Util Functions
//

function build_formatted_JSON_tag(data) {
  return $("<pre></pre>").text(JSON.stringify(data, null, 4));
}

// Channel Tab
function load_channels(event) {
  insert_spinner("#channels", "primary");
  let table = $("#channels > table > tbody");
  table.empty();
  let channel_template;
  $.ajax($("#channels-table").attr("data-template-endpoint"))
    .done((data) => {
      channel_template = document.createElement("tr");
      channel_template.innerHTML = data;
    })
    .fail((data) => {
      console.log(data);
    })
    .then(() => {
      $.getJSON(buildURL("api_admin.channel"))
        .done((data) => {
          data.forEach((element) => {
            let row = channel_template.cloneNode(true);

            row.dataset.channelId = element.id;
            row.getElementsByClassName("channel-name")[0].innerText =
              element.name;
            row
              .getElementsByClassName("channel-name")[0]
              .parentElement.setAttribute(
                "href",
                buildURL("main.channel", { channel_id: element.id })
              );
            row.getElementsByClassName("channel-id")[0].innerText = element.id;
            row.getElementsByClassName(
              "channel-id"
            )[0].parentElement.dataset.clipboardText = element.id;

            let status = row.getElementsByClassName("channel-status")[0];
            status.innerHTML = "";
            status.appendChild(
              generate_callback_status_badge(element.hub_infos.state)
            );

            row.getElementsByClassName("channel-expiration")[0].innerText =
              element.hub_infos.expiration;
            row.getElementsByClassName(
              "channel-expiration-badge"
            )[0].innerText = moment(element.hub_infos.expiration).fromNow();
            table.append(row);
          });
          init_clipboard();
          $(".btn-refresh").click(channel_refresh);
        })
        .fail((data) => {
          console.log(data);
        });
    })
    .fail((data) => {
      console.log(data);
    })
    .always(() => {
      drop_spinner("#channels");
    });
}

function channel_refresh(event) {
  let button = $(event.target);
  let channel_row = button.parent().parent();
  let status = channel_row.find(".channel-status");
  let expiration = channel_row.find(".expiration");
  const channel_id = channel_row.data("channel-id");

  button.empty().attr({ disabled: true });
  status.empty();
  expiration.empty();
  insert_spinner(button, "secondary", true);
  insert_spinner(status, "secondary", true);
  insert_spinner(expiration, "secondary", true);

  $.ajax({
    type: "get",
    url: buildURL("api_channel.status", { channel_id: channel_id }),
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
  let celery_task_template;
  $.ajax($("#celery-table").attr("data-template-endpoint")).done((data) => {
    celery_task_template = document.createElement("tr");
    celery_task_template.innerHTML = data;
  });
  $.getJSON($("#celery-table").attr("data-api-endpoint")).done((data) => {
    data.forEach((element) => {
      let row = celery_task_template.cloneNode(true);
      let task_name_tag = `<p class="mb-0">${element.request.id}</p><p class="mb-0 text-muted">#${element.request.name}</p>`;
      row.getElementsByClassName("task-name")[0].innerHTML = task_name_tag;
      row.getElementsByClassName("task-args")[0].innerText = JSON.stringify(
        element.request.args
      );
      row.getElementsByClassName("task-eta")[0].innerText = moment(
        element.eta
      ).fromNow();
      let task_active_tag = row.getElementsByClassName("task-active")[0];
      for (child of task_active_tag.childNodes) {
        task_active_tag.removeChild(child);
      }
      if (element.active) {
        task_active_tag.innerHTML =
          '<span class="badge bg-success">Active</span>';
      } else {
        task_active_tag.innerHTML =
          '<span class="badge bg-danger">Revoked</span>';
      }
      table.append(row);
    });
    drop_spinner("#celery_tasks");
  });
}

function empty_results(event) {
  $("#management > .results").empty();
}

function load_notifications(event) {
  insert_spinner("#notifications", "primary");
  let table = $("#notifications > table > tbody");
  table.empty();
  let notification_template;
  $.ajax($("#notifications-table").attr("data-template-endpoint"))
    .done((data) => {
      notification_template = document.createElement("tr");
      notification_template.innerHTML = data;
    })
    .fail((data) => {
      console.log(data);
    })
    .then(() => {
      $.getJSON(buildURL("api_admin.notifications"))
        .done((data) => {
          data.forEach((element) => {
            let row = notification_template.cloneNode(true);
            if (element.kwargs.image_url) {
              const image_tag = document.createElement("img");
              image_tag.src = element.kwargs.image_url;
              image_tag.className = "rounded";
              image_tag.setAttribute("width", 200);
              row.getElementsByClassName("image")[0].appendChild(image_tag);
            }

            row.getElementsByClassName("sent-timestamp")[0].innerText =
              element.sent_timestamp;
            row.getElementsByClassName("title")[0].innerText =
              element.kwargs.title;
            row.getElementsByClassName("message")[0].dataset.bsContent =
              element.message;
            new bootstrap.Popover(row.getElementsByClassName("message")[0]);

            if (element.kwargs.url) {
              const url_tag = document.createElement("a");
              url_tag.href = element.kwargs.url;
              url_tag.innerText = element.kwargs.url_title
                ? element.kwargs.url_title
                : element.kwargs.url;
              row.getElementsByClassName("url")[0].appendChild(url_tag);
            }

            if (element.response && element.response.status) {
              const button_tag = document.createElement("button");
              button_tag.setAttribute("type", "button_tag");
              button_tag.classList.add("response-btn", "btn");
              button_tag.classList.add(
                element.response.status === 1 ? "btn-success" : "btn-danger"
              );
              button_tag.setAttribute("data-bs-container", "body");
              button_tag.setAttribute("data-bs-toggle", "popover");
              button_tag.setAttribute("data-bs-placement", "right");
              button_tag.setAttribute("data-bs-trigger", "focus");
              button_tag.setAttribute(
                "data-bs-content",
                element.response.request
              );
              button_tag.innerText =
                element.response.status === 1 ? "OK" : "Error";
              const status_badge = document.createElement("span");
              status_badge.classList.add("badge", "bg-light", "text-dark");
              status_badge.innerText = element.response.status;
              button_tag.appendChild(status_badge);
              row.getElementsByClassName("response")[0].appendChild(button_tag);
              new bootstrap.Popover(button_tag);
            }
            table.append(row);
          });
        })
        .fail((data) => {
          console.log(data);
        });
    })
    .fail((data) => {
      console.log(data);
    })
    .always(() => {
      drop_spinner("#notifications");
    });
}

$(document).ready(() => {
  // Tab activate
  $("#channels-tab").on("shown.bs.tab", load_channels);
  $("#celery_tasks-tab").on("shown.bs.tab", load_tasks);
  $("#management-tab").on("shown.bs.tab", empty_results);
  $("#notifications-tab").on("shown.bs.tab", load_notifications);
  // Channel page
  $("#btn-refresh-all").click(() => {
    $(".btn-refresh").click();
  });
  // Management page
  $("#channel-renew-all").click(api_with_progress);
  $("#channel-renew-all-schedule").click(api_get);
  $("#channel-renew-all-random").click(api_get);
  $("#task-remove-all").click(api_get);
});
