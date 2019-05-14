$(document).ready(function() {
    $(".renew-btn").each(function() {
        $(this).click(function(event) {
            var badge = $("<span></span>").attr({
                "class": "spinner-border spinner-border-sm",
                "role": "status",
                "aria-hidden": "true"
            })
            $(this).empty().attr({
                "class": "btn btn-secondary renew-btn",
                "disabled": "true"
            }).append(badge);
            var renew_link = $(this).attr("data-renew-url");
            var self = $(this)
            $.ajax({
                type: "get",
                url: renew_link
            }).done(function(responseData) {
                self.parent().empty().text(JSON.stringify(responseData))
            }).fail(function(responseData, self) {
                self.parent().empty().text(responseData)
            });
        });
    });
});