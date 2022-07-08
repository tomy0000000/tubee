const VALID_SPINNER_TYPE = [
  "primary",
  "secondary",
  "success",
  "danger",
  "warning",
  "info",
  "light",
  "dark",
];

const CLIPBOARD_SELECTOR = ".clipboard";

// ---------------
// Util Functions
// ---------------

/**
 * @param {String} HTML representing any number of sibling elements
 * @return {NodeList|Element} A list of elements or a single element
 */
function html_to_elements(html) {
  let template = document.createElement("template");
  template.innerHTML = html.trim();
  if (template.content.childNodes.length > 1) {
    return template.content.childNodes;
  } else {
    return template.content.firstChild;
  }
}

async function fetch_simple_get(endpoint, params = {}, text = false) {
  const query_string = new URLSearchParams(params);
  const url = `${endpoint}?${query_string}`;

  const response = await fetch(url);
  if (!response.ok) {
    alert(`Error: ${response.statusText}`);
    throw new Error(response.statusText);
  }

  if (text) {
    return await response.text();
  } else {
    return await response.json();
  }
}

async function fetch_post_form(endpoint, form, text = false) {
  const response = await fetch(endpoint, {
    method: "POST",
    body: new FormData(form),
  });
  if (!response.ok) {
    alert(`Error: ${response.statusText}`);
    throw new Error(response.statusText);
  }

  if (text) {
    return await response.text();
  } else {
    return await response.json();
  }
}

function new_btn_set_loading(button) {
  button.disabled = true;
  const spinner = html_to_elements(
    `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>`
  );
  button.appendChild(spinner);
}

function new_btn_unset_loading(button) {
  button.disabled = false;
  let spinner = button.querySelector(".spinner-border");
  button.removeChild(spinner);
}

function set_loading(button) {
  let spinner_id = Date.now();
  $(button)
    .append(
      $("<span>").attr({
        id: spinner_id,
        class: "spinner-border spinner-border-sm",
      })
    )
    .data({ "spinner-id": spinner_id })
    .prop("disabled", true);
}

function unset_loading(button) {
  drop_spinner(button);
  button.prop("disabled", false);
}

function insert_spinner(location, type, small = false) {
  type = VALID_SPINNER_TYPE.includes(type) ? type : "primary";
  let size = small ? "spinner-border-sm" : "";
  let spinner_id = Date.now();
  $(location)
    .append(
      $("<div>")
        .attr({
          id: spinner_id,
          class: `spinner-border text-${type} ${size}`,
        })
        .append($("<span>").addClass("sr-only").text("Loading..."))
    )
    .data({ "spinner-id": spinner_id });
}

function drop_spinner(location) {
  let spinner_id = $(location).data("spinner-id");
  $(location).find(`#${spinner_id}`).remove();
}

function build_url(endpoint, path_params = {}) {
  const raw_sitemap = JSON.parse(document.body.dataset.sitemap);
  const key_based_sitemap = {};
  Object.keys(raw_sitemap).forEach((blueprint) => {
    raw_sitemap[blueprint].map((route) => {
      key_based_sitemap[route[1]] = route[0];
    });
  });

  let url = key_based_sitemap[endpoint];
  Object.keys(path_params).forEach((key) => {
    url = url.replace(`<${key}>`, path_params[key]);
  });

  return url;
}

function generate_callback_status_badge(status) {
  const BADGE_TYPE_MAPPING = {
    verified: "success",
    expired: "danger",
    unverified: "warning",
    unsubscribed: "secondary",
  };
  let badge_type =
    status in BADGE_TYPE_MAPPING ? BADGE_TYPE_MAPPING[status] : "info";
  let badge = $("<span></span>")
    .addClass(`badge bg-${badge_type}`)
    .text(status);
  return badge;
}

function generate_callback_type_badge(type) {
  const BADGE_TYPE_MAPPING = {
    "Hub Notification": "success",
    "Hub Challenge": "warning",
  };
  let badge_type =
    type in BADGE_TYPE_MAPPING ? BADGE_TYPE_MAPPING[type] : "info";
  let badge = $("<span></span>").addClass(`badge bg-${badge_type}`).text(type);
  console.log(badge);
  return badge;
}

// ---------------
// Init Functions
// ---------------

function init_clipboard() {
  new ClipboardJS(CLIPBOARD_SELECTOR);
  $(`${CLIPBOARD_SELECTOR} p`)
    .tooltip({
      placement: "right",
      title: "Copied!",
      trigger: "click",
    })
    .on("mouseleave", function () {
      $(this).tooltip("hide");
    })
    .on("click", (event) => {
      event.preventDefault();
    });
}

function init_popover() {
  // $('[data-toggle="popover"]').popover();
  var popoverTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="popover"]')
  );
  var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
    return new bootstrap.Popover(popoverTriggerEl);
  });
}

// ---------------
// Toolbar
// ---------------

async function submit_subscribe(event) {
  // UI
  new_btn_set_loading(event.target);

  // API
  const api_endpoint = document.getElementById("navbar-subscribe-submit")
    .dataset.subscribeApi;
  let form = document.getElementById("navbar-subscribe-form");
  await fetch_post_form(api_endpoint, form);

  // Redirect
  location.href = $("#navbar-main").attr("href");
}

$(document).ready(() => {
  init_clipboard();
  init_popover();

  $(".subscribe-submit").click(submit_subscribe);

  let channel_search_api = $("#channel_id").data("channel-api");
  $("#channel_id").autoComplete({
    resolverSettings: {
      url: channel_search_api,
      queryKey: "query",
      requestThrottling: 1000,
    },
    formatResult: (item) => {
      return {
        value: item.id,
        text: item.id,
        html: [
          $("<div>")
            .addClass("d-flex align-items-center")
            .append(
              $("<div>").append(
                $("<img>")
                  .attr({
                    class: "rounded-circle",
                    src: item.thumbnail,
                  })
                  .css("height", "2rem")
              ),
              $("<div>").append($("<p>").addClass("mb-0 ml-2").text(item.title))
            ),
        ],
      };
    },
  });
});
