(function ($) {
  $.fn.updateChannelId = function () {
    const channelId = this.data("channel-id");
    const formId = this.data("form-id");
    $(`#${formId}`).find("input")[0].value = channelId;
    return this;
  };
})(jQuery);
