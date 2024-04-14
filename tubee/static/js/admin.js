//
// Util Functions
//

function loadChannelPage(event) {
  $("#channels")
    .empty()
    .addLoadingSpinner({})
    .load(buildURL("admin.channels"), function () {
      init_moment();
      init_clipboard();
      $(this).find("table").DataTable();
      $(this).dropLoadingSpinner({});
    });
}

$(document).ready(() => {
  // Tab activate
  $("#channels-tab").on("shown.bs.tab", loadChannelPage);
});
