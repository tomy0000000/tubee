$(document).ready(function() {
    // Hub Status
    $.ajax({
        type: 'get',
        url: $('#status-grid').attr('data-api-endpoint'),
    }).done(function(responseData) {
        console.log(responseData)
        let state = responseData.state;
        if (state === 'verified') {
            let badge = $('<span></span>').addClass('badge badge-success').text(state);
            $('#state').empty().append(badge);
        } else if (state === 'expired') {
            let badge = $('<span></span>').addClass('badge badge-danger').text(state);
            $('#state').empty().append(badge);
        } else if (state === 'unverified') {
            let badge = $('<span></span>').addClass('badge badge-info').text(state);
            $('#state').empty().append(badge);
        } else if (state === 'unsubscribed') {
            let badge = $('<span></span>').addClass('badge badge-secondary').text(state);
            $('#state').empty().append(badge);
        } else {
            $('#state').text(state);
        }
        $('#expiration').text(responseData.expiration);
        $('#last-notification').text(responseData.last_notification);
        $('#last-notification-error').text(responseData.last_notification_error);
        $('#last-challenge').text(responseData.last_challenge);
        $('#last-challenge-error').text(responseData.last_challenge_error);
        $('#last-subscribe').text(responseData.last_subscribe);
        $('#last-unsubscribe').text(responseData.last_unsubscribe);
        $('#stat').text(responseData.stat);
    }).fail(function(responseData) {
        console.log('Request Failed');
    }).always(function(responseData) {
        console.log('Request Sent');
    });

    // Action Modals
    $('#edit_action_modal').on('show.bs.modal', function(event) {
        let button = $(event.relatedTarget); // Button that triggered the modal
        let action_id = button.data('action-id'); // Extract info from data-* attributes
        // If necessary, you could initiate an AJAX request here (and then do the updating in a callback).
        // Update the modal's content. We'll use jQuery here, but you could use a data binding library or other methods instead.
        if (action_id === 'new') {
            $(this).find('.modal-title').text('New Action');
            // $(this).find('.modal-body input').val(recipient)
        } else {
            $('#edit_action_modal_spinner').show();
            $('#action_form').hide();
            $.get(`/api/${action_id}`).done(function(data) {
                $('#action_name').val(data.action_name);
                $('#action_type').val(data.action_type);
                $('#edit_action_modal_spinner').hide();
                $('#action_form').show();
            });
            $(this).find('.modal-title').text('Edit Action');
        }
    });
});
