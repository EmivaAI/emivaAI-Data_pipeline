def handle_slack_webhook(data, headers):
    from database.db import save_raw_data
    
    # Slack URL verification challenge
    if data.get('type') == 'url_verification':
        return {"challenge": data.get('challenge')}, 200
        
    event_type = data.get('type', 'event_callback')
    if event_type == 'event_callback':
        event_type = data.get('event', {}).get('type', 'unknown')
        
    save_raw_data('slack', data, event_type=event_type)
    return {"status": "success"}, 200
