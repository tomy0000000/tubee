function refresh_action_fields(type) {
  $(".action-type-fields").hide();
  if (type === "Notification") {
    $(".notification-fields").show();
  } else if (type === "Playlist") {
    $(".playlist-fields").show();
  } else if (type === "Download") {
    $(".download-fields").show();
  } else {
    console.log("Unknown Type");
  }
}
