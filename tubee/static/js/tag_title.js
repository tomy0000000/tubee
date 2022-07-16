$(document).ready(() => {
  $(".btn-title-edit").each(function () {
    $(this).click((event) => {
      event.preventDefault();
      $(".rename-blocks").toggle();
    });
  });
});
