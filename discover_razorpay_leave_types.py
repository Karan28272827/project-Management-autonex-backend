import json
import os

from dotenv import load_dotenv

from app.api.leaves import post_razorpay_attendance


def main() -> None:
    load_dotenv()

    sample_email = os.getenv("RAZORPAY_DISCOVERY_EMAIL", "sample_email@testmail.com")
    sample_date = os.getenv("RAZORPAY_DISCOVERY_DATE", "2026-03-17")

    request_body = {
        "request": {
            "type": "attendance",
            "sub-type": "modify",
        },
        "data": {
            "email": sample_email,
            "date": sample_date,
            "status": "leave",
            "leave-type": -1,
        },
    }

    response_text = post_razorpay_attendance(request_body)
    print("Razorpay discovery response:")
    print(response_text or "<empty response>")
    print()
    print("Map the returned leave-type IDs in backend/.env, for example:")
    print("RAZORPAY_LEAVE_TYPE_CASUAL=2")
    print("RAZORPAY_LEAVE_TYPE_SICK=1")
    print("RAZORPAY_LEAVE_TYPE_VACATION=0")


if __name__ == "__main__":
    main()
