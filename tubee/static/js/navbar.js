$(document).ready(() => {
  const url = buildURL("api_channel.search");
  $("#channel_id").autoComplete({
    resolverSettings: {
      url,
      queryKey: "query",
      requestThrottling: 1000,
    },
    formatResult: (response) => {
      let item = response.content;
      return {
        value: item.id,
        text: item.id,
        html: [
          $("<div>")
            .addClass(["d-flex", "align-items-center"])
            .append(
              $("<div>").append(
                $("<img>")
                  .addClass("rounded-circle")
                  .attr("src", item.thumbnail)
                  .css("height", "2rem")
              ),
              $("<div>").append(
                $("<p>").addClass(["mb-0", "ml-2"]).text(item.title)
              )
            ),
        ],
      };
    },
  });
});
