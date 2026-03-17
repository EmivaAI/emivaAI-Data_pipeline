import re
import json
from database.db import Session, RawWebhookData, ChangeEvent
from sqlalchemy import or_

def extract_jira_keys(text):
    """Extracts Jira keys like EMIVA-123 from text."""
    if not text:
        return []
    return re.findall(r'[A-Z]+-\d+', text)

def determine_change_type(jira_issue_type, pr_labels, pr_title, summary=""):
    """Logic provided by user to determine change type."""
    # Priority 1: Jira issue type
    mapping = {
        "Bug":         "bug_fix",
        "Story":       "feature", 
        "Task":        "chore",
        "Epic":        "feature",
        "Improvement": "feature",
    }
    if jira_issue_type in mapping:
        return mapping[jira_issue_type]
    
    # Priority 2: Summary/Title keywords
    full_text = f"{pr_title if pr_title else ''} {summary if summary else ''} {jira_issue_type if jira_issue_type else ''}".lower()
    if full_text.startswith("bug") or "fix" in full_text: return "bug_fix"
    if full_text.startswith("feat"): return "feature"
    if full_text.startswith("chore"): return "chore"
    if "critical" in full_text: return "bug_fix"
    if "docs" in full_text: return "docs"
    
    # Priority 3: PR title prefix
    if pr_title:
        title = pr_title.lower()
        if title.startswith("fix"):      return "bug_fix"
        if title.startswith("feat"):     return "feature"
        if title.startswith("chore"):    return "chore"
        if title.startswith("docs"):     return "docs"
        if title.startswith("refactor"): return "chore"
    
    # Priority 4: PR labels
    if pr_labels:
        if "bug" in pr_labels:     return "bug_fix"
        if "feature" in pr_labels: return "feature"
    
    return "unknown"

def process_unprocessed_events():
    session = Session()
    try:
        # 1. Selection: Fetch all RawWebhookData where processed=False
        unprocessed_events = session.query(RawWebhookData).filter(RawWebhookData.processed == False).all()
        if not unprocessed_events:
            print("No new events to process.")
            return

        print(f"Processing {len(unprocessed_events)} new events...")

        # Group events by Jira Key
        jira_to_events = {}
        processed_ids = []
        orphan_events = []

        # First pass: map Jira events and find common keys
        for event in unprocessed_events:
            keys = []
            if event.source == 'jira':
                issue_key = event.payload.get('issue', {}).get('key')
                if issue_key:
                    keys.append(issue_key)
            else:
                # Search in payload for mentions
                text_to_search = ""
                if event.source == 'github':
                    text_to_search = event.payload.get('pull_request', {}).get('title', '') + " " + \
                                     event.payload.get('pull_request', {}).get('body', '')
                elif event.source == 'slack':
                    text_to_search = event.payload.get('event', {}).get('text', '')
                
                keys = extract_jira_keys(text_to_search)

            if keys:
                for key in set(keys):
                    if key not in jira_to_events:
                        jira_to_events[key] = []
                    jira_to_events[key].append(event)
            else:
                orphan_events.append(event)
            
            processed_ids.append(event.id)

        # 2. Process Jira-grouped events
        for key, events in jira_to_events.items():
            consolidate_and_save(session, events, key)

        # 3. Process orphans (e.g. PRs without Jira keys)
        for event in orphan_events:
            if event.source == 'github' and 'pull_request' in event.payload:
                consolidate_and_save(session, [event], None)
            else:
                # Other orphans (like Slack messages or Github stars) might not be "changes"
                # For now, mark them processed but don't create a ChangeEvent unless they are PRD relevant
                pass

        # 4. State Management: Mark as processed
        session.query(RawWebhookData).filter(RawWebhookData.id.in_(processed_ids)).update({"processed": True}, synchronize_session=False)
        session.commit()
        print("Processing complete.")

    except Exception as e:
        session.rollback()
        print(f"Error during processing: {e}")
    finally:
        session.close()

def consolidate_and_save(session, events, jira_key):
    source_ids = [e.id for e in events]
    
    # Extract data from events
    jira_event = next((e for e in events if e.source == 'jira'), None)
    github_event = next((e for e in events if e.source == 'github' and 'pull_request' in e.payload), None)
    slack_events = [e for e in events if e.source == 'slack']
    
    summary = "Consolidated Event"
    change_type = "unknown"
    component = "Unknown"
    severity = "medium"
    linked_issues = [jira_key] if jira_key else []
    linked_prs = []
    linked_threads = []
    actors = set()
    raw_signals = {
        "pr_merged": False,
        "issue_resolved": False,
        "has_slack_discussion": len(slack_events) > 0
    }
    
    # Use Jira as source of truth if available
    if jira_event:
        issue = jira_event.payload.get('issue', {})
        fields = issue.get('fields', {})
        summary = fields.get('summary', summary)
        component = fields.get('project', {}).get('name', component)
        severity = fields.get('priority', {}).get('name', 'medium').lower()
        actors.add(jira_event.payload.get('user', {}).get('displayName'))
        
        jira_issue_type = fields.get('issuetype', {}).get('name')
        change_type = determine_change_type(jira_issue_type, [], "", summary=summary)
        
        status = fields.get('status', {}).get('name')
        if status in ['Done', 'Resolved', 'Closed']:
            raw_signals['issue_resolved'] = True

    # Layer Github info
    if github_event:
        pr = github_event.payload.get('pull_request', {})
        if not jira_event:
            summary = pr.get('title', summary)
            component = github_event.payload.get('repository', {}).get('name', component)
        
        linked_prs.append(pr.get('number'))
        actors.add(pr.get('user', {}).get('login'))
        
        if change_type == "unknown":
            labels = [l.get('name') for l in pr.get('labels', [])]
            change_type = determine_change_type(None, labels, pr.get('title'), summary=summary)
            
        if pr.get('merged') or github_event.payload.get('action') == 'closed':
             raw_signals['pr_merged'] = True

    # Layer Slack info
    for se in slack_events:
        thread_ts = se.payload.get('event', {}).get('thread_ts')
        if thread_ts:
            linked_threads.append(thread_ts)
        actors.add(se.payload.get('event', {}).get('user'))

    # Check if a ChangeEvent for this Jira key already exists to update it
    existing_change = None
    if jira_key:
        existing_change = session.query(ChangeEvent).filter(ChangeEvent.linked_issues.contains(jira_key)).first()

    if existing_change:
        # Update existing
        existing_change.source_event_ids = list(set(existing_change.source_event_ids + source_ids))
        existing_change.linked_prs = list(set(existing_change.linked_prs + linked_prs))
        existing_change.linked_threads = list(set(existing_change.linked_threads + linked_threads))
        existing_change.actors = list(set(existing_change.actors + list(filter(None, actors))))
        existing_change.raw_signals.update(raw_signals)
        print(f"Updated ChangeEvent for {jira_key}")
    else:
        # Create new
        new_change = ChangeEvent(
            source_event_ids=source_ids,
            change_type=change_type,
            component=component,
            summary=summary,
            severity=severity,
            linked_issues=linked_issues,
            linked_prs=linked_prs,
            linked_threads=linked_threads,
            actors=list(filter(None, actors)),
            raw_signals=raw_signals
        )
        session.add(new_change)
        print(f"Created new ChangeEvent for {jira_key or 'Orphan'}")

if __name__ == "__main__":
    process_unprocessed_events()
