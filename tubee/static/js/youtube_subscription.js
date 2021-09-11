var row_template;
const table = document.getElementById("subscription-table");
const spinner = document.getElementById("loading-spinner");

async function subscribe_in_import(event) {
  // UI
  const button = event.target;
  new_btn_set_loading(button);

  const api_endpoint = document.getElementById("navbar-subscribe-submit")
    .dataset.subscribeApi;
  let form = document.getElementById("navbar-subscribe-form");
  form.channel_id.value = button.dataset.channelId;

  try {
    await fetch_post_form(api_endpoint, form);
  } catch (error) {
    new_btn_unset_loading(button);
    button.classList = ["btn-danger"];
    button.innerText = "Error";
  }

  new_btn_unset_loading(button);
  button.disabled = true;
  button.innerText = "Subscribed";
}

function build_row(snippet) {
  let row = row_template.cloneNode(true);
  let channel_id = snippet.resourceId.channelId;
  row.querySelector(".channel-thumbnails").src = snippet.thumbnails.medium.url;
  row.querySelector(".channel-name").innerText = snippet.title;
  row.querySelector(".channel-id-a").dataset.clipboardText = channel_id;
  row.querySelector(".channel-id-p").innerText = channel_id;
  if (!snippet.subscribed) {
    let button = html_to_elements(`
      <button
        class="btn btn-success subscribe-submit"
        type="button"
        data-channel-id="${snippet.resourceId.channelId}"
      >
        Subscribe
      </button>
    `);
    button.addEventListener("click", subscribe_in_import);
    row.querySelector(".channel-subscribed").appendChild(button);
  }
  return row;
}

async function load_more() {
  spinner.style.display = "block";
  let api_endpoint = table.dataset.apiEndpoint;
  let params = table.dataset.nextPageToken
    ? {
        page_token: table.dataset.nextPageToken,
      }
    : {};

  // Get subscriptions
  try {
    var response = await fetch_simple_get(api_endpoint, params);
  } catch (error) {
    spinner.style.display = "none";
  }

  // Build row for each channel
  response.items.forEach((channel) => {
    let row = build_row(channel.snippet);
    table.getElementsByTagName("tbody")[0].appendChild(row);
  });

  // Store nextPageToken to table
  if (response.nextPageToken) {
    table.dataset.nextPageToken = response.nextPageToken;
    table.addEventListener("load-more", load_more, {
      once: true,
    });
  }

  // Unload spinner
  spinner.style.display = "none";

  // Initialize Clipboard JS
  init_clipboard();
}

// Load more on scroll
window.addEventListener("scroll", (event) => {
  let trigger_row = table.querySelector("tr:nth-last-child(10)");
  let rect = trigger_row.getBoundingClientRect();
  if (rect.bottom <= window.innerHeight) {
    var loading_event = new CustomEvent("load-more");
    table.dispatchEvent(loading_event);
  }
});

document.addEventListener("DOMContentLoaded", async (event) => {
  // Load row template
  const template_endpoint = table.dataset.channelRowEndpoint;
  row_template = html_to_elements(
    await fetch_simple_get(template_endpoint, {}, true)
  );

  // Load first page
  load_more();
});
