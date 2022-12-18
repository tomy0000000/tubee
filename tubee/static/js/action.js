(function ($) {
  $.fn.refresh_field = function () {
    const type = $(this).find("#action_type").val().toLowerCase();
    $(".action-type-fields").hide();
    $(".action-type-fields input:required")
      .prop("required", false)
      .attr("data-required", true);
    $(`.${type}-fields`).show();
    $(`.${type}-fields input[data-required]`).prop("required", true);
  };

  $.fn.actionModal = function () {
    const action_id = $(this).data("action-id");
    const channel_id = $(this).data("channel-id");
    const tag_id = $(this).data("tag-id");
    let modalPath;
    if (action_id) {
      modalPath = buildURL("action.form_read", { action_id });
    } else {
      modalPath = buildURL("action.form_empty");
    }
    $("#hidden-container").load(
      modalPath,
      function (responseText, textStatus, jqXHR) {
        if (textStatus === "success") {
          const modal = $(this).find(".action-form-modal");
          modal.find("form").refresh_field();
          if (!action_id) {
            if (!channel_id && !tag_id) {
              modal.find(".automate-fields").hide();
            } else {
              modal.find("#channel_id").val(channel_id);
              modal.find("#tag_id").val(tag_id);
            }
          }
          modal.modal("show");
        }
      },
    );
    return this;
  };
})(jQuery);
