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

// ---------------
// Util Functions
// ---------------

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

function buildURL(endpoint, path_params = {}, query_params = {}) {
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
  if (params) {
    url = `${url}?${params}`;
  }

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

// ---------------
// Init Functions
// ---------------

function init_clipboard() {
  const CLIPBOARD_SELECTOR = ".clipboard";
  new ClipboardJS(CLIPBOARD_SELECTOR);
  $(`${CLIPBOARD_SELECTOR} p`)
    .tooltip({
      placement: "right",
      title: "Copied!",
      trigger: "click",
    })
    .click((event) => {
      event.preventDefault();
    })
    .mouseleave(function () {
      $(this).tooltip("hide");
    });
}

function init_popover() {
  $('[data-toggle="popover"]').popover();
}

$(document).ready(() => {
  init_clipboard();
  init_popover();
});
