"""DM ATSC Collector."""

import argparse
import copy
import json
import re
from typing import (
    Any,
    Dict,
    List,
    Literal,
    NotRequired,
    Optional,
    Self,
    TypedDict,
    Union,
    Unpack,
)

import requests
from requests.exceptions import RequestException

TIMEOUT = 10.0


class NMSDeviceNamesParams(TypedDict):
    """Type Definition for NMS Device Names"""

    server: str
    version: NotRequired[Literal["vistalink", "nms"]]


class DMCollectorParams(TypedDict):
    """Type Definition DM Collector Parameters"""

    ip: str
    slots: List[int]
    username: NotRequired[str]
    password: NotRequired[str]
    nms: NotRequired[NMSDeviceNamesParams]
    legacy: NotRequired[bool]


class JSONRPCRequest(TypedDict):
    """Type Definition JSON RPC Request"""

    jsonrpc: Literal["2.0"]
    method: str
    params: Dict[str, Any]
    id: Union[int, str]


class JSONRPCParameter(TypedDict):
    """Type Definition JSON RPC Parameter."""

    id: str
    type: Literal["string", "integer", "float"]
    name: str
    value: NotRequired[Union[str, int, float]]


class JSONRPCResponse(TypedDict):
    """Type Definition JSON RPC Response."""

    jsonrpc: Literal["2.0"]
    result: Dict[Literal["parameters"], List[JSONRPCParameter]]
    id: Union[int, str]


class Demod(TypedDict, total=False):
    """Type Definition Demodulator information"""

    s_input_tag: str
    s_input_status: str
    i_input_power: int
    i_input_mer: int
    i_input: int
    i_slot: int
    s_card_type: str
    s_card_label: str
    s_frame_label: str
    as_ids: List[int]


# Type Definition Demod Card
Card = TypedDict(
    "Card",
    {"1": Demod, "2": Demod, "3": Demod, "4": Demod},
)

# Type Definition for Frame
Frame = TypedDict(
    "Frame",
    {
        "2": Optional[Card],
        "3": Optional[Card],
        "4": Optional[Card],
        "5": Optional[Card],
        "6": Optional[Card],
        "7": Optional[Card],
        "8": Optional[Card],
        "9": Optional[Card],
        "10": Optional[Card],
        "11": Optional[Card],
        "12": Optional[Card],
        "13": Optional[Card],
        "14": Optional[Card],
        "15": Optional[Card],
    },
)


class NMSAPIResponse(TypedDict):
    """Type Definition NMS API Response"""

    result: str


class ElementNotFound(Exception):
    """Exception for missing element in NMS Response"""


class APIEndpointError(Exception):
    """Exception for NMS API Endpoint errors."""


class NMSDeviceNames:
    """VistaLINK NMS Device Name Collector"""

    def __init__(
        self,
        server: str,
        frame: str,
        version: Literal["vistalink", "nms"] = "vistalink",
    ) -> None:
        self.ip = frame
        self.api_url = f"http://{server}:8082/{version}/1/hardware/<replace>/label.json"

        self.slots: List[str | None] = [None for _ in range(16)]
        self.frame = None

        try:
            # Fetch slot labels
            for slot in range(2, 16):
                response = self.fetch(self.get_url(self.api_url, f"{self.ip}:{slot}"))
                if response is not None:
                    # remove the [#] prefix from the label
                    result = re.sub(r"\[\d+\]\s*", "", response["result"]).strip()
                    self.slots[slot] = result

            # Fetch frame label
            frame_response = self.fetch(self.get_url(self.api_url, self.ip))
            if frame_response is not None:
                self.frame = frame_response["result"]

        except (RequestException, json.JSONDecodeError) as error:
            print(f"Error during NMS Device Name fetch: {error}")

    def fetch(self, url: str) -> Union[NMSAPIResponse, None]:
        """Fetch data from NMS server."""

        try:
            with requests.Session() as session:
                response = session.get(url=url, timeout=TIMEOUT)

                if response.status_code == 404:
                    raise APIEndpointError(f"Code:{response.status_code}")

                if response.status_code != 200:
                    raise ElementNotFound(
                        f"{response.text} Code:{response.status_code}"
                    )

                return json.loads(response.text)

        except RequestException as req_error:
            print(f"Network error during request: {req_error}")
            raise
        except json.JSONDecodeError as json_error:
            print(f"Error decoding JSON response: {json_error}")
            raise
        except APIEndpointError as api_error:
            print(f"API endpoint error: {api_error}")
            raise
        except ElementNotFound:
            return None
        except Exception as error:
            print(f"Unexpected error in fetch: {error}")
            raise

    def get_url(self, url: str, replace: str) -> str:
        """Get URL with replacement."""
        return url.replace("<replace>", replace)

    def get_slot(self, slot: int) -> Optional[str]:
        """Get slot label from NMS server."""
        return self.slots[slot]

    def get_frame(self) -> Optional[str]:
        """Get the frame label from NMS Server"""
        return self.frame


class DMCollector:
    """7880DM4-ATSC Demodulator Input Collector for 7800 Frames"""

    SLOT: JSONRPCParameter = {
        "id": "36.<replace>@s",
        "type": "string",
        "name": "Product Name",
    }

    TAG: JSONRPCParameter = {
        "id": "150.<replace>@s",
        "type": "string",
        "name": "s_input_tag",
    }
    LOCK: JSONRPCParameter = {
        "id": "120.<replace>@i",
        "type": "integer",
        "name": "s_input_status",
    }
    POWER: JSONRPCParameter = {
        "id": "121.<replace>@i",
        "type": "integer",
        "name": "i_input_power",
    }
    MER: JSONRPCParameter = {
        "id": "126.<replace>@i",
        "type": "integer",
        "name": "i_input_mer",
    }

    def __init__(self, **kwargs: Unpack[DMCollectorParams]) -> None:
        # Frame information
        self.ip = "localhost"
        self.slots: List[int] = []
        self.legacy = False

        # Credentials for web easy
        self.username = "root"
        self.password = "evertz"

        # NMS
        self.nms: NMSDeviceNamesParams | None = None
        self.nms_names: NMSDeviceNames | None = None

        # Unpack kwargs to instance variables with defaults
        for key, value in kwargs.items():
            setattr(self, key, value)

        # API URLs for frame controller and cards
        self.card_url = f"http://{self.ip}/slot/<replace>/htdocs/cgi-bin/cfgjsonrpc"
        self.frame_url = f"http://{self.ip}/v.1.5/php/datas/cfgjsonrpc.php"

        # If legacy flag is set, use the older frame URL structure
        if self.legacy:
            self.frame_url = f"http://{self.ip}/cgi-bin/cfgjsonrpc"

        self.card_parameters: List[JSONRPCParameter] = []
        self.frame_parameters: List[JSONRPCParameter] = []

        # generate card query parameters for 4 ports
        for port in range(4):
            for param in [self.TAG, self.LOCK, self.POWER, self.MER]:
                c = copy.deepcopy(param)
                c["id"] = c["id"].replace("<replace>", str(port))
                self.card_parameters.append(c)

        # generate query parameters to discover cards in each slot
        for slot in range(2, 16):
            s = copy.deepcopy(self.SLOT)
            s["id"] = s["id"].replace("<replace>", str(slot))
            self.frame_parameters.append(s)

        # Initialize parent NMS Name Collector
        if self.nms is not None:
            self.nms_names = NMSDeviceNames(
                server=self.nms["server"],
                frame=self.ip,
                version=self.nms.get("version", "vistalink"),
            )

    @classmethod
    def auto_discover(cls, card: str, **kwargs: Unpack[DMCollectorParams]) -> Self:
        """Auto discover cards in frame."""
        instance = cls(**kwargs)

        try:
            response = instance.fetch(instance.frame_url, instance.frame_parameters)

            for param in response["result"]["parameters"]:
                try:
                    slot = int(param["id"].split(".")[1].split("@")[0])
                    product_name = param.get("value", "")
                    if card in str(product_name):
                        instance.slots.append(slot + 1)

                except (KeyError, ValueError, IndexError) as error:
                    print(f"Error processing parameter {param}: {error}")
                    continue

        except (RequestException, json.JSONDecodeError) as error:
            print(f"Error during AutoCardDiscover: {error}")

        return instance

    def fetch(self, url: str, parameters: List[JSONRPCParameter]) -> JSONRPCResponse:
        """Fetch data from DM device."""
        try:

            with requests.Session() as session:

                session.auth = (self.username, self.password)

                payload: JSONRPCRequest = {
                    "jsonrpc": "2.0",
                    "method": "get",
                    "params": {"parameters": parameters},
                    "id": 1,
                }

                headers = {"Content-Type": "application/x-www-form-urlencoded"}

                response = session.post(
                    url=url,
                    headers=headers,
                    data=json.dumps(payload),
                    verify=False,
                    timeout=TIMEOUT,
                )

                return json.loads(response.text)

        except RequestException as req_error:
            print(f"Network error during request: {req_error}")
            raise
        except json.JSONDecodeError as json_error:
            print(f"Error decoding JSON response: {json_error}")
            raise
        except Exception as error:
            print(f"Unexpected error in fetch: {error}")
            raise

    def get_url(self, url: str, replace: str) -> str:
        """Get URL with replacement."""
        return url.replace("<replace>", replace)

    def annotate_nms_names(self, card: Card) -> None:
        """Annotate card with NMS names."""
        if self.nms_names is None:
            return

        for port in range(1, 5):
            slot = card[str(port)]["i_slot"]

            if (slot_name := self.nms_names.get_slot(slot)) is not None:
                card[str(port)]["s_card_label"] = slot_name

            if (frame_name := self.nms_names.get_frame()) is not None:
                card[str(port)]["s_frame_label"] = frame_name

            card[str(port)]["s_card_type"] = "7880DM4-ATSC"

    def collect_card(self, slot: int) -> Card:
        """Collect data from a specific card slot."""
        url = self.get_url(self.card_url, str(slot))

        card: Card = {
            "1": {"as_ids": [], "i_input": 1, "i_slot": slot},
            "2": {"as_ids": [], "i_input": 2, "i_slot": slot},
            "3": {"as_ids": [], "i_input": 3, "i_slot": slot},
            "4": {"as_ids": [], "i_input": 4, "i_slot": slot},
        }

        # Annotate with NMS custom names if available
        self.annotate_nms_names(card)

        response = self.fetch(url, self.card_parameters)

        for param in response["result"]["parameters"]:
            try:
                # seperate "240.1@i" to "1@i"
                _id = param["id"].split(".")[1]

                # split the instance and type notation, then convert the
                # instance back to base 1 for port number
                instance = _id.split("@")[0]
                instance = str(int(instance) + 1)

                # resolve the lock status enumeration
                if "input_status" in param["name"]:
                    if param.get("value") == 1:
                        param["value"] = "Locked"
                    else:
                        param["value"] = "Not Locked"

                # perform a dict update key/value
                card[instance].update(
                    {
                        param["name"]: param.get("value", None),
                    }
                )

                # add the id to the list of as_ids
                card[instance]["as_ids"].append(param["id"])

            except (KeyError, ValueError, IndexError) as error:
                print(f"Error processing parameter {param}: {error}")
                continue

        return card

    def run(self) -> Frame:
        """Collect data from DM device."""
        frame: Frame = {
            "2": None,
            "3": None,
            "4": None,
            "5": None,
            "6": None,
            "7": None,
            "8": None,
            "9": None,
            "10": None,
            "11": None,
            "12": None,
            "13": None,
            "14": None,
            "15": None,
        }

        for slot in self.slots:
            try:
                frame[str(slot)] = self.collect_card(slot)

            except (KeyError, ValueError, IndexError) as error:
                print(f"Error collecting slot {slot}: {error}")
                continue
            except Exception as error:  # pylint: disable=W0718:broad-exception-caught
                print(f"Unexpected error in collect_card for slot {slot}: {error}")
                continue

        return frame


def main():
    """Main function."""

    # Argument Parser
    args_parser = argparse.ArgumentParser(
        description="7880DM4-ATSC Input RF Power Level Collector"
    )

    args_parser.add_argument(
        "-ip",
        "--frame-ip",
        required=True,
        type=str,
        metavar="<192.168.1.2>",
        help="IP Address of the 7800 Frame",
    )
    args_parser.add_argument(
        "-u",
        "--username",
        required=False,
        type=str,
        metavar="<root>",
        default="root",
        help="Username for frame web access",
    )
    args_parser.add_argument(
        "-p",
        "--password",
        required=False,
        type=str,
        metavar="<evertz>",
        default="evertz",
        help="Password for frame web access",
    )
    args_parser.add_argument(
        "-nms",
        "--magnum-nms",
        required=False,
        type=str,
        metavar="<ip>",
        help="IP Address of the NMS Server for custom names (optional)",
    )
    args_parser.add_argument(
        "-legacy",
        "--legacy-frame",
        required=False,
        action="store_true",
        help="Use the legacy frame URL structure (optional)",
    )

    args = args_parser.parse_args()

    params: DMCollectorParams = {
        "ip": args.frame_ip,
        "slots": [],
        "username": args.username,
        "password": args.password,
        "legacy": args.legacy_frame,
    }

    if args.magnum_nms is not None:
        params["nms"] = {"server": args.magnum_nms}

    # Auto discover cards in frame
    collector = DMCollector.auto_discover("7880DM4-ATSC", **params)

    # Run the collector
    frame = collector.run()

    documents = []
    for _, card in frame.items():
        if card is None or not isinstance(card, dict):
            continue

        for _, instance in card.items():
            document = {"fields": instance, "host": params["ip"], "name": "rf_demod"}
            documents.append(document)

    print(json.dumps(documents, indent=4))


if __name__ == "__main__":
    main()
