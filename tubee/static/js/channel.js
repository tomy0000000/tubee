function edit_modal_load(action_id) {
    $('#edit_save_spinner').hide();
    $('#edit_action_modal').find('#submit').prop("disabled", false);
    let api_endpoint;

    if (action_id === 'new') {
        $('#edit_action_modal').find('.modal-title').text('New Action');
        api_endpoint = '/api/action/new';
        $('#action_type').prop('disabled', false);
        $('#edit_loading_spinner').hide();
    } else {
        $('#edit_action_modal').find('.modal-title').text('Edit Action');
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
    return api_endpoint;
}

$(document).ready(function() {
    // Hub Status
    $.ajax({
        type: 'get',
        url: $('#status-grid').attr('data-api-endpoint'),
    }).done(function(responseData) {
        let state = responseData.state;
        let badge;
        switch (state) {
            case 'verified':
                badge = $('<span></span>').addClass('badge badge-success').text(state);
                $('#state').empty().append(badge);
                break;
            case 'expired':
                badge = $('<span></span>').addClass('badge badge-danger').text(state);
                $('#state').empty().append(badge);
                break;
            case 'unverified':
                badge = $('<span></span>').addClass('badge badge-info').text(state);
                $('#state').empty().append(badge);
                break;
            case 'unsubscribed':
                badge = $('<span></span>').addClass('badge badge-secondary').text(state);
                $('#state').empty().append(badge);
                break;
            default:
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
        console.log("Hub Status Request Failed");
        $('#state').text("Error");
        $('#expiration').text("Error");
        $('#last-notification').text("Error");
        $('#last-notification-error').text("Error");
        $('#last-challenge').text("Error");
        $('#last-challenge-error').text("Error");
        $('#last-subscribe').text("Error");
        $('#last-unsubscribe').text("Error");
        $('#stat').text("Error");
    });

    // Edit Action Modals
    $('#edit_action_modal').on('show.bs.modal', function(event) {
        let button = $(event.relatedTarget); // Button that triggered the modal
        let action_id = button.data('action-id'); // Extract info from data-* attributes        
        let api_endpoint = edit_modal_load(action_id);
        $(this).find('#submit').on('click', function(event) {
            // Appearence
            event.preventDefault();
            $('#edit_save_spinner').show();
            $(this).prop("disabled", true);
            $('#action_form').serializeArray();
            // Request
            $.post(api_endpoint, $('#action_form').serializeArray(), function(data, textStatus, xhr) {
                console.log(data);
            }).done(function(responseData) {
                console.log(Boolean(responseData));
                if (Boolean(responseData)) {
                    $('#edit_action_modal').modal('hide');
                    location.reload();
                } else {
                    alert('Save Failed, Try Again');
                    edit_modal_load();
                }
            }).fail(function(responseData) {
                alert('Save Failed, Try Again');
                edit_modal_load();
            });
        });
    });

    // Remove Action Modals
    $('#remove_action_modal').on('show.bs.modal', function(event) {
        let button = $(event.relatedTarget);
        let action_id = button.data('action-id');
        let action_name = button.data('action-name');
        // Appearence
        $('#remove_spinner').hide();
        $(this).prop("disabled", false);
        $(this).find('.modal-body').text(`Are you sure you want to remove action ${action_name}?`);
        $('#remove_button').on('click', function(event) {
            // Appearence
            event.preventDefault();
            $('#remove_spinner').show();
            $(this).prop("disabled", true);
            // Request
            $.get(`/api/${action_id}/remove`).done(function(data) {
                console.log(Boolean(data));
                if (Boolean(data)) {
                    $('#remove_action_modal').modal('hide');
                    location.reload();
                } else {
                    alert('Remove Failed, Try Again');
                }
            });
        });
    });
});
