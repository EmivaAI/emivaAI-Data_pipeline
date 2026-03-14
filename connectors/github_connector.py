def handle_github_webhook(data, headers):
    from database.db import save_raw_data
    event_type = headers.get('X-GitHub-Event', 'unknown')
    save_raw_data('github', data, event_type=event_type)
    return {"status": "success"}, 200
