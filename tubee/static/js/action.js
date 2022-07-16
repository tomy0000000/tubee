(function ($) {
  $.fn.refresh_field = function () {
    const type = $(this).find("#action_type").val().toLowerCase();
    $(".action-type-fields").hide();
    $(`.${type}-fields`).show();
  };

  $.fn.actionModal = function () {
    const action_id = $(this).data("action-id");
    const channel_id = $(this).data("channel-id");
    const tag_id = $(this).data("tag-id");
    let modalPath;
    if (action_id) {
      modalPath = buildURL("action.read", { action_id });
    } else {
      modalPath = buildURL("action.empty");
    }
    $("#hidden-container").load(
      modalPath,
      function (responseText, textStatus, jqXHR) {
        if (textStatus === "success") {
          const modal = $(this).find(".action-form-modal");
          modal.find("form").refresh_field();
          if (!action_id) {
            modal.find("#channel_id").val(channel_id);
            modal.find("#tag_id").val(tag_id);
          }
          modal.modal("show");
        }
      }
    );
    return this;
  };
})(jQuery);
