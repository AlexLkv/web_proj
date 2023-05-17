import dataclasses
import requests
import re
import logging

log = logging.getLogger("SMS")

@dataclasses.dataclass()
class TSMSResponse:
    id: str = "0"
    status: int = 0
    status_code: int = -1
    balance: float = 0


class SMSTransport:
    _URL = "https://sms.ru/sms/send"

    def __init__(self):
        self._api_id = "726D9207-F648-26F9-E45D-E52479E9791F"

    def send(self, to: str, msg: str) -> TSMSResponse:
        if not self.validate_phone(to):
            log.error("Invalid phone number")
            return TSMSResponse()

        response = requests.get(self._URL, params=dict(
            api_id=self._api_id,
            to=to,
            msg=f"Ваш код подтверждения-{msg}",
            json=1
        )).json()

        log.debug("Response %s", response)

        if response["status"] == "OK":
            phone = response["sms"][to]

            if phone["status"] == "OK":
                return TSMSResponse(
                    status=1,
                    status_code=phone["status_code"],
                    balance=response['balance'],
                    id=phone["sms_id"]
                )

        log.debug("Error status %s", response)
        return TSMSResponse(
            status_code=response["status_code"]
        )

    @classmethod
    def validate_phone(cls, phone):
        return re.match(r"^7[0-9]{10}$", phone)