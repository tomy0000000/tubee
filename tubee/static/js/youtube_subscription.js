var row_template;
const table = $("#subscription-table");

function build_row(snippet) {
  const row = row_template.clone();
  const channel_id = snippet.resourceId.channelId;
  row.find(".thumbnails").attr("src", snippet.thumbnails.medium.url);
  row.find(".name").text(snippet.title);
  row.find(".id-anchor").data("clipboard-text", channel_id);
  row.find(".id-text").text(channel_id);
  if (snippet.subscribed) {
    row.find(".subscribe").empty();
  } else {
    const section = row.find(".subscribe");
    section.children("form").attr("id", `${channel_id}-subscribe-form`);
    section.find("input").val(channel_id);
    section.find("button").data("form-id", `${channel_id}-subscribe-form`);
  }
  return row;
}

function load_more(event) {
  const spinner = $("#loading-spinner");
  const url = buildURL(table.data("api"));
  const params = { page_token: table.data("next-page-token") };
  spinner.show();

  // Get subscriptions
  $.getJSON(url, params)
    .then((response) => {
      if (!response.ok) {
        return $.Deferred().reject(response.error);
      }
      return response.content;
    })
    .done((response) => {
      // Build row for each channel
      response.items.forEach((channel) => {
        const row = build_row(channel.snippet);
        table.children("tbody").append(row);
      });

      // Store nextPageToken to table
      if (response.nextPageToken) {
        table
          .data("next-page-token", response.nextPageToken)
          .one("load-more", load_more);
      }

      // Initialize Clipboard JS
      init_clipboard();
    })
    .always(() => {
      spinner.hide();
    });
}

$(document).ready((event) => {
  // Load row template
  const url = buildURL("static", {
    filename: "component/youtube_subscription/table_row.html",
  });
  $.get(url).done((data) => {
    row_template = $(data);
  });

  // Load more on scroll
  $(window).on("scroll", (event) => {
    const trigger_row = table.find("tr:nth-last-child(10)");
    if (trigger_row.isInViewport()) {
      table.trigger("load-more");
    }
  });

  // Load first page
  load_more();
});
