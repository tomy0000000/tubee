var row_template;
const table = $("#subscription-table");

async function subscribe_in_import(event) {
  // UI
  const button = $(event.target);
  button.buttonToggleState({ state: "loading" });

  const url = build_url($("#navbar-subscribe-submit").data("api"));
  let form = document.getElementById("navbar-subscribe-form");
  form.channel_id.value = button.data("channel-id");

  try {
    await fetch_post_form(url, form);
  } catch (error) {
    button.buttonToggleState({ state: "fail", error: error.message });
  }

  button.buttonToggleState({ state: "success" });
}

function build_row(snippet) {
  const row = row_template.clone();
  const channel_id = snippet.resourceId.channelId;
  row.find(".thumbnails").attr("src", snippet.thumbnails.medium.url);
  row.find(".name").text(snippet.title);
  row.find(".id-anchor").data("clipboard-text", channel_id);
  row.find(".id-text").text(channel_id);
  if (!snippet.subscribed) {
    const button = $("<button>")
      .addClass(["subscribe-submit", "btn", "btn-success"])
      .attr("type", "button")
      .data("channel-id", channel_id)
      .text("Subscribe")
      .on("click", subscribe_in_import);
    row.find(".subscribed").append(button);
  }
  return row;
}

function load_more(event) {
  const spinner = $("#loading-spinner");
  const url = build_url(table.data("api"));
  const params = { page_token: table.data("next-page-token") };
  spinner.show();

  // Get subscriptions
  $.getJSON(url, params)
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
  const url = table.data("channel-row-endpoint");
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
