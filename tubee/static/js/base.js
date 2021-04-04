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

function generate_callback_badge(status) {
  const BADGE_TYPE_MAPPING = {
    verified: "success",
    expired: "danger",
    unverified: "warning",
    unsubscribed: "secondary",
  };
  let badge_type =
    status in BADGE_TYPE_MAPPING ? BADGE_TYPE_MAPPING[status] : "info";
  let badge = $("<span></span>")
    .addClass(`badge badge-${badge_type}`)
    .text(status);
  return badge;
}

function register_clipboard_items(selector) {
  new ClipboardJS(selector);
  $(`${selector} p`)
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

function submit_subscribe(event) {
  // UI
  let icon = $("<span>").attr({
    class: "spinner-border spinner-border-sm mr-1",
    role: "status",
    "aria-hidden": true,
  });
  let text = $("<span>").addClass("aria-hidden").text("Loading...");
  $(event.currentTarget).prop("disabled", true).empty().append(icon, text);

  // API
  let is_navbar =
    $(event.currentTarget).attr("id") === "navbar-subscribe-submit"; // false for youtube subscription
  let api_endpoint = $("#navbar-subscribe-submit").data("subscribe-api");
  let channel_id = is_navbar
    ? $("#subscribe-input").val()
    : $(event.currentTarget).data("channel-id");
  api_endpoint = api_endpoint.replace(encodeURI("<channel_id>"), channel_id);
  $.ajax({
    type: "GET",
    url: api_endpoint,
    success: (response) => {
      if (response) {
        if (is_navbar) {
          location.href = $("#navbar-main").attr("href");
        } else {
          icon.remove();
          $(event.currentTarget).prepend(
            $("<i>").addClass("fas fa-check mr-1")
          );
          text.text("Done!");
          console.log(response);
        }
      } else {
        alert("Something went wrong");
        if (is_navbar) {
          location.reload();
        } else {
          $(event.currentTarget)
            .removeClass("btn-success")
            .addClass("btn-danger");
          icon.remove();
          $(event.currentTarget).prepend(
            $("<i>").addClass("fas fa-times mr-1")
          );
          text.text("Error");
          console.log(response);
        }
      }
    },
  });
}

$(document).ready(() => {
  register_clipboard_items(".clipboard");
  $(".subscribe-submit").click(submit_subscribe);

  let channel_search_api = $("#subscribe-input").data("channel-api");
  $("#subscribe-input").autoComplete({
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
