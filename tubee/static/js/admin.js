//
// Util Functions
//

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

$(document).ready(() => {
  // Tab activate
  $("#channels-tab").on("shown.bs.tab", loadChannelPage);
  $("#celery_tasks-tab").on("shown.bs.tab", load_tasks);
});
