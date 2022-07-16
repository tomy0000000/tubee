(function ($) {
  // --------------------
  // Global helper functions
  // --------------------

  $.fn.isInViewport = function () {
    // Check if the element is in the viewport
    let elementTop = $(this).offset().top;
    let elementBottom = elementTop + $(this).outerHeight();

    let viewportTop = $(window).scrollTop();
    let viewportBottom = viewportTop + $(window).height();

    return elementBottom > viewportTop && elementTop < viewportBottom;
  };

  $.fn.serializeObject = function () {
    let object = {};
    const array = this.serializeArray();
    $.map(array, (pair) => {
      object[pair.name] = pair.value;
    });
    return object;
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
    let spinnerId = Date.now(); // This id is used to drop the spinner later

    const spinnerSpan = $("<span>")
      .addClass("visually-hidden")
      .text("Loading...");
    const spinnerContainer = $("<div>")
      .attr("id", spinnerId)
      .attr("role", "status")
      .addClass(["spinner-border", `text-${type}`, size])
      .append(spinnerSpan);

    this.append(spinnerContainer).data({ "spinner-id": spinnerId });
    return this;
  };

  $.fn.dropLoadingSpinner = function () {
    let spinnerId = this.data("spinner-id");
    if (spinnerId) {
      this.find(`#${spinnerId}`).remove();
    }
    return this;
  };

  // --------------------
  // Confirm Modal
  // --------------------

  $.fn.confirm = function (event, message) {
    event.preventDefault();
    const button = $(event.target);
    const modalPath = buildURL("static", {
      filename: "component/confirm_modal.html",
    });
    $("#hidden-container").load(modalPath, function () {
      const modal = $("#confirm-modal");
      const modalMessage = message
        ? `Are your sure you want to ${message}?`
        : "Are you sure?";
      modal.find(".modal-body").text(modalMessage);
      modal.find(".btn-confirm").click(function () {
        modal.modal("hide");
        const callback = button.data("callback");
        button[callback]();
      });
      modal.modal("show");
    });
    return this;
  };

  // --------------------
  // Button Methods
  // --------------------

  $.fn.buttonAPI = function () {
    const api = this.data("api");
    const method = this.data("api-method");
    const formId = this.data("form-id");
    const pathParams = this.data("path-params");
    const queryParams = this.data("query-params");

    const url = buildURL(api, pathParams, queryParams);
    const form_data = formId ? $(`#${formId}`).serializeObject() : {};
    const data = JSON.stringify(form_data);

    this.buttonToggleState({ state: "loading" });
    $.ajax({ url, method, data, contentType: "application/json" })
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
        .prop("disabled", true)
        .addLoadingSpinner({ type: "secondary", small: true });
    } else if (state === "success") {
      this.empty().text("Done").dropLoadingSpinner();
    } else if (state === "fail") {
      this.empty().text(error).dropLoadingSpinner();
    }
    return this;
  };
})(jQuery);
