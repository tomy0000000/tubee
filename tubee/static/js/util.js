(function ($) {
  // --------------------
  // Global helper functions
  // --------------------

  $.fn.isInViewport = function () {
    var elementTop = $(this).offset().top;
    var elementBottom = elementTop + $(this).outerHeight();

    var viewportTop = $(window).scrollTop();
    var viewportBottom = viewportTop + $(window).height();

    return elementBottom > viewportTop && elementTop < viewportBottom;
  };

  // --------------------
  // Spinner
  // --------------------

  $.fn.addLoadingSpinner = function ({ type = "primary", small = false }) {
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
    type = type.toLowerCase();
    type = VALID_SPINNER_TYPE.includes(type) ? type : "primary";
    let size = small ? "spinner-border-sm" : "";
    let spinner_id = Date.now(); // This id is used to drop the spinner later

    const spinner_span = $("<span>")
      .addClass("visually-hidden")
      .text("Loading...");
    const spinner_container = $("<div>")
      .attr("id", spinner_id)
      .attr("role", "status")
      .addClass(["spinner-border", `text-${type}`, size])
      .append(spinner_span);

    this.append(spinner_container).data({ "spinner-id": spinner_id });
    return this;
  };

  $.fn.dropLoadingSpinner = function () {
    let spinner_id = this.data("spinner-id");
    if (spinner_id) {
      this.find(`#${spinner_id}`).remove();
    }
    return this;
  };

  // --------------------
  // Button Methods
  // --------------------

  $.fn.buttonCallGetApi = function () {
    const api = this.data("api");
    const path_params = this.data("path-params");
    const query_params = this.data("query-params");
    const url = build_url(api, path_params, query_params);

    this.buttonToggleState({ state: "loading" });
    $.ajax({ type: "get", url })
      .done((responseData) => {
        this.buttonToggleState({ state: "success" });
      })
      .fail((responseData) => {
        this.buttonToggleState({ state: "fail", error: responseData });
      });
  };

  $.fn.buttonToggleState = function ({ state, error }) {
    if (state === "loading") {
      this.empty()
        .attr({ disabled: true })
        .addLoadingSpinner({ type: "secondary", small: true });
    } else if (state === "success") {
      this.empty().text("Done").dropLoadingSpinner();
    } else if (state === "fail") {
      this.empty().text(error).dropLoadingSpinner();
    }
    return this;
  };
})(jQuery);
