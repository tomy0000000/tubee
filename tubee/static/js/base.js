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

function build_url(endpoint, path_params = {}, query_params = {}) {
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

  const params = $.param(query_params);
  url = `${url}?${params}`;

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
  let badge = document.createElement("span");
  badge.classList.add("badge", `bg-${badge_type}`, "text-dark");
  badge.innerText = status;
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
  const elements = document.querySelectorAll(`${CLIPBOARD_SELECTOR} p`);
  const tooltipList = [...elements].map((element) => {
    const tooltip = new bootstrap.Tooltip(element, {
      placement: "right",
      title: "Copied!",
      trigger: "click",
    });
    element.addEventListener("mouseleave", (event) => {
      tooltip.hide();
    });
    return tooltip;
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
  $(event.target).buttonToggleState({ state: "loading" });

  // API
  const url = build_url($("#navbar-subscribe-submit").data("api"));
  let form = document.getElementById("navbar-subscribe-form");
  await fetch_post_form(url, form);

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
