(function ($) {
  $.fn.updateVideoIds = function () {
    $(".btn-all-checked").data("api-query-params", {
      video_ids: table
        .data()
        .map((row) => row[5])
        .join(),
    });
    console.log($(".btn-all-checked").data("api-query-params"));
    return this;
  };

  $.fn.reloadTable = function () {
    setTimeout(() => {
      table.ajax.reload();
    }, 500);
    return this;
  };
})(jQuery);
