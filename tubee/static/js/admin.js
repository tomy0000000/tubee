//
// Util Functions
//

function build_formatted_JSON_tag(data) {
  return $("<pre></pre>").text(JSON.stringify(data, null, 4));
}

function loadChannelPage(event) {
  $("#channels")
    .empty()
    .addLoadingSpinner({})
    .load(buildURL("admin.channels"), function () {
      init_moment();
      init_clipboard();
      $(this).find("table").DataTable();
      $(this).dropLoadingSpinner({});
    });
}

function update_progress(status_url, progress_bar, message_box) {
  // send GET request to status URL
  $.getJSON(status_url)
    .then((response) => {
      if (!response.ok) {
        return $.Deferred().reject(response.error);
      }
      return response.content;
    })
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
          `Currently Processing: ${data.result.channel_name} <${data.channel_id}>`,
        );
        setTimeout(
          update_progress,
          2000,
          status_url,
          progress_bar,
          message_box,
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
  const url = buildURL("api_channel.renew_all");
  $.getJSON(url)
    .then((response) => {
      if (!response.ok) {
        return $.Deferred().reject(response.error);
      }
      return response.content;
    })
    .done((data) => {
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
        message_box,
      );
      setTimeout(update_progress, 2000, data.status, progress_bar, message_box);
    });
}

function api_get(event) {
  event.preventDefault();
  insert_spinner("#management", "primary");
  const api = $(this).data("api");
  const pathParams = $(this).data("path-params");
  const url = buildURL(api, pathParams);
  $.getJSON(url).done((data) => {
    $("#management > .results").append(
      $("<pre>").text(JSON.stringify(data, null, 2)),
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
  $.ajax(
    buildURL("static", { filename: "component/admin/celery_table_row.html" }),
  ).done((data) => {
    celery_task_template = document.createElement("tr");
    celery_task_template.innerHTML = data;
  });
  $.getJSON(buildURL("api_task.list_all"))
    .then((response) => {
      if (!response.ok) {
        return $.Deferred().reject(response.error);
      }
      return response.content;
    })
    .done((data) => {
      data.forEach((element) => {
        let row = celery_task_template.cloneNode(true);
        let task_name_tag = `<p class="mb-0">${element.request.id}</p><p class="mb-0 text-muted">#${element.request.name}</p>`;
        row.getElementsByClassName("task-name")[0].innerHTML = task_name_tag;
        row.getElementsByClassName("task-args")[0].innerText = JSON.stringify(
          element.request.args,
        );
        row.getElementsByClassName("task-eta")[0].innerText = moment(
          element.eta,
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

$(document).ready(() => {
  // Tab activate
  $("#channels-tab").on("shown.bs.tab", loadChannelPage);
  $("#celery_tasks-tab").on("shown.bs.tab", load_tasks);
  $("#management-tab").on("shown.bs.tab", empty_results);
  // Management page
  $("#channel-renew-all").click(api_with_progress);
  $("#channel-renew-all-schedule").click(api_get);
  $("#channel-renew-all-random").click(api_get);
  $("#task-remove-all").click(api_get);
});
