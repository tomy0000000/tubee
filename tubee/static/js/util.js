// --------------------
// Spinner
// --------------------

$.fn.addLoadingSpinner = ({ type = "primary", small = false }) => {
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

$.fn.dropLoadingSpinner = () => {
  let spinner_id = this.data("spinner-id");
  if (spinner_id) {
    this.find(`#${spinner_id}`).remove();
  }
  return this;
};

// --------------------
// Button Methods
// --------------------

$.fn.buttonToggleLoading = () => {
  this.empty()
    .attr({ disabled: true })
    .addLoadingSpinner({ type: "secondary", small: true });
  return this;
};

$.fn.buttonToggleSuccess = () => {
  this.empty().text("Done").dropLoadingSpinner();
  return this;
};

$.fn.buttonToggleFail = (error) => {
  this.empty().text(error).dropLoadingSpinner();
  return this;
};
