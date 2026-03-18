from database.db import save_raw_data

class WebhookService:
    @staticmethod
    def process_webhook_data(source_type, raw_payload, workspace_id="default-workspace"):
        """
        Process incoming webhook data and persist it to the database.
        This acts as the service layer between the API and the DB.
        """
        # Additional logic (validation, queueing, etc.) can be added here
        save_raw_data(source_type, raw_payload, workspace_id=workspace_id)
        return {"status": "success"}, 200

webhook_service = WebhookService()
