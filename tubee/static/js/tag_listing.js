$(document).ready(() => {
  const sortable = $("#tag-sortable");
  sortable.sortable({
    axis: "x",
    items: "> .sortable",
    disabled: true,
  });

  $("#btn-sort").click((event) => {
    event.preventDefault();
    const button = $(event.currentTarget);
    button.find("i").toggleClass("fa-edit").toggleClass("fa-save");

    const mode = button.data("mode");
    if (!mode || mode === "saved") {
      sortable.sortable("enable");
      button.data("mode", "edit");
    } else {
      sortable.sortable("disable");

      const tagIds = $.map(sortable.find(".sortable"), function (element) {
        return $(element).data("tag-id");
      });
      $("#sort-index-form > input[name=order]").val(tagIds.join(","));

      button
        .data("mode", "saved")
        .data("api-endpoint", "api_tag.update_sort_indexes")
        .data("api-method", "PATCH")
        .data("api-form-id", "sort-index-form")
        .data("api-restore", true)
        .buttonAPI();
    }
  });
});
