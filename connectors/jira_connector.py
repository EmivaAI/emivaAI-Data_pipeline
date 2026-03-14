def handle_jira_webhook(data, headers):
    from database.db import save_raw_data
    event_type = data.get('webhookEvent', 'unknown')
    save_raw_data('jira', data, event_type=event_type)
    return {"status": "success"}, 200
