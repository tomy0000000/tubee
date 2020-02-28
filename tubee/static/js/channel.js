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

    // Edit Action Modals
    $('#edit_action_modal').on('show.bs.modal', function(event) {
        let button = $(event.relatedTarget); // Button that triggered the modal
        let action_id = button.data('action-id'); // Extract info from data-* attributes
        
        $('#edit_save_spinner').hide();
        $(this).find('#submit').prop("disabled", false);
        let api_endpoint;

        if (action_id === 'new') {
            $(this).find('.modal-title').text('New Action');
            api_endpoint = '/api/action/new';
            $('#action_type').prop('disabled', false);
            $('#edit_loading_spinner').hide();
        } else {
            $(this).find('.modal-title').text('Edit Action');
            api_endpoint = '/api/action/edit';
            $('#edit_loading_spinner').show();
            $('#action_form').hide();
            $.get(`/api/${action_id}`).done(function(data) {
                $('#action_name').val(data.action_name);
                $('#action_type').val(data.action_type).prop('disabled', true);
                $('#edit_loading_spinner').hide();
                $('#action_form').show();
            });
        }
        $(this).find('#submit').on('click', function(event) {
            $(this).find('#edit_save_spinner').show();
            $(this).prop("disabled", true);
            $('#action_form').serializeArray();
            $.post(api_endpoint, $('#action_form').serializeArray(), function(data, textStatus, xhr) {
                console.log(data);
            });
        });
    });

    // Remove Action Modals
    $('#remove_action_modal').on('show.bs.modal', function(event) {
        let button = $(event.relatedTarget);
        let action_id = button.data('action-id');
        let action_name = button.data('action-name');
        $(this).find('.modal-body').text(`Are you sure you want to remove action ${action_name}?`);
        $(this).find('#remove_button').attr('href', `/api/${action_id}/remove`);
    });
});
