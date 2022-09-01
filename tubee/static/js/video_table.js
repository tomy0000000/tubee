function updateBtnAllChecked(datatable) {
  $(".btn-all-checked").attr(
    "data-query-params",
    JSON.stringify({
      video_ids: datatable
        .api()
        .data()
        .map((row) => row[5])
        .join(),
    }),
  );
}
