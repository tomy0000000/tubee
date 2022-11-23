(function ($) {
  // --------------------
  // Global helper functions
  // --------------------

  // $.fn.isInViewport = function () {
  //   // Check if the element is in the viewport
  //   let elementTop = $(this).offset().top;
  //   let elementBottom = elementTop + $(this).outerHeight();

  //   let viewportTop = $(window).scrollTop();
  //   let viewportBottom = viewportTop + $(window).height();

  //   return elementBottom > viewportTop && elementTop < viewportBottom;
  // };

  $.fn.serializeObject = function () {
    let object = {};
    const array = this.serializeArray();
    $.map(array, (pair) => {
      object[pair.name] = JSON.parse(pair.value);
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

  $.fn.confirm = function () {
    const button = $(this);
    const message = button.data("confirm-message");
    const modalPath = buildURL("static", {
      filename: "component/confirm_modal.html",
    });
    $("#hidden-container").load(modalPath, function () {
      const modal = $("#confirm-modal");
      const modalMessage = message
        ? `Are your sure you want to ${message}?`
        : "Are you sure?";
      modal.find(".modal-body").text(modalMessage);
      // Copy API data to modal confirm button
      const confirmButton = modal
        .find(".btn-confirm")
        .attr("onclick", "$(this).buttonAPI()");
      $.each(button.data(), (key, value) => {
        if (key.startsWith("api") && key !== "apiConfirm") {
          confirmButton.data(key, value);
        }
      });
      modal.modal("show");
    });
    return this;
  };

  // --------------------
  // Button Methods
  // --------------------

  $.fn.buttonAPI = function () {
    const endpoint = this.data("api-endpoint");
    const method = this.data("api-method");
    const formId = this.data("api-form-id");
    const pathParams = this.data("api-path-params");
    const queryParams = this.data("api-query-params");
    const confirm = this.data("api-confirm");
    const restore = this.data("api-restore");

    if (confirm) {
      return this.confirm();
    }

    const url = buildURL(endpoint, pathParams, queryParams);
    const form_data = formId ? $(`#${formId}`).serializeObject() : {};
    const data = JSON.stringify(form_data);

    this.buttonToggleState({ state: "loading" });
    $.ajax({ url, method, data, contentType: "application/json" })
      .then((response) => {
        if (!response.ok) {
          return $.Deferred().reject(response.description);
        }
        return response.content;
      })
      .done((responseData) => {
        this.buttonToggleState({ state: "success" });
        if (restore) {
          const button = this;
          setTimeout(() => {
            button.buttonToggleState({ state: "restore" });
          }, 3000);
        }
      })
      .fail((responseData) => {
        this.buttonToggleState({
          state: "fail",
          error: responseData.responseJSON.description,
        });
      });
    return this;
  };

  $.fn.buttonToggleState = function ({ state, error }) {
    const lastState = this.data("backup-state");
    if (state === "restore") {
      this.replaceWith(lastState);
      return this;
    }
    if (!lastState) {
      this.data("backup-state", this.clone(true));
    }
    if (state === "loading") {
      this.empty()
        .prop("disabled", true)
        .addLoadingSpinner({ type: "secondary", small: true });
    } else if (state === "success") {
      this.empty().text("Done").dropLoadingSpinner();
    } else if (state === "fail") {
      this.empty().addClass("btn-danger").text(error).dropLoadingSpinner();
    }
    return this;
  };
})(jQuery);
