$(document).ready(() => {
  $(".btn-title-edit").each(function () {
    $(this).click((event) => {
      event.preventDefault();
      $("#title-block").toggle();
      $("#rename-block").toggle();
    });
  });
});
