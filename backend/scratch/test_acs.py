import os
import asyncio
from dotenv import load_dotenv
from backend.services.email_service import email_service

async def test_email():
    load_dotenv()
    recipient = os.getenv("APPROVAL_RECIPIENT", "Raghavendra.Lakkamaraju@valuemomentum.com")
    print(f"Initiating ACS Handshake...")
    print(f"Target Recipient: {recipient}")
    
    subject = "ACS System Test: BA Agent Pro Connectivity"
    body = """
       System Connectivity Test
    This is an automated test message from the <strong>BA Agent Pro</strong> orchestration engine.
    <strong>Status:</strong> Validating Azure Communication Services (ACS) Handshake
    <strong>Environment:</strong> Development
    <hr/>
    If you have received this email, your governance notification system is correctly configured.
    """
    
    try:
        # Use the synchronous notification wrapper we created earlier
        email_service.send_approval_notification(subject, body)
        print("SUCCESS: ACS Email Handshake initiated successfully.")
        print("Check your inbox for the validation message.")
    except Exception as e:
        print(f"FAILURE: ACS Email Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_email())
