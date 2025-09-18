# inSITE 7880DM4-ATSC RF Demodulator Collector

Collector for the 7880DM4-ATSC Demodulator RF input power level collector. Poller script has integration with VistaLINK PRO (Magnum NMS) to annotate card and frame custom descriptions. This script is capable of collecting the demodulator input RF power level for all cards in a single 7800 Frame.

## Minimum Requirements:

-   inSITE Version 12 and service pack 5
-   Ubuntu 22.04

## Installation:

Installation of the status monitoring module requires copying two scripts into the poller modules folder:

1. Copy **dm_atsc_collector.py** script to the poller python modules folder:

    ```
     cp scripts/dm_atsc_collector.py /opt/evertz/insite/parasite/applications/pll-1/data/python/modules
    ```

2. Restart the poller application

## Configuration:

To configure a poller to use the module start a new python poller configuration outlined below

1. Click the create a custom poller from the poller application settings page
2. Enter a Name, Summary and Description information
3. Enter the host value in the _Hosts_ tab
4. From the _Input_ tab change the _Type_ to **Python**
5. From the _Input_ tab change the _Metric Set Name_ field to **rfdemod**
6. From the _Python_ tab select the _Advanced_ tab and enable the **CPython Bindings** option
7. Select the _Script_ tab, then paste the contents of **scripts/poller_config.py** into the script panel.

8. Locate the below section of the script for custom modifcations:

    ```
        params: DMCollectorParams = {
            "ip": host,
            "slots": [],
            "nms": {"server": "nms-server-ip", "version": "vistalink"},
        }
    ```

    Replace the nms-server-ip value with the IP address of the VistaLINK/Magnum NMS system. Replace "vistalink" with "nms" if Magnum Analytics is installed

9. Save changes, then restart the poller program.

## Usage:

```
python-insite dm_atsc_collector.py -h
```

```
usage: dm_atsc_collector.py [-h] -ip <192.168.1.2> [-u <root>] [-p <evertz>] [-nms <ip>]

7880DM4-ATSC Input RF Power Level Collector

options:
  -h, --help            show this help message and exit
  -ip <192.168.1.2>, --frame-ip <192.168.1.2>
                        IP Address of the 7800 Frame
  -u <root>, --username <root>
                        Username for frame web access
  -p <evertz>, --password <evertz>
                        Password for frame web access
  -nms <ip>, --magnum-nms <ip>
                        IP Address of the NMS Server for custom names (optional)
```

## Testing:

The process_monitor script can be ran manually from the shell using the following command

```
python-insite dm_atsc_collector.py -ip <fc-ip> -nms <nms-ip>
```

Below is the sample json file created:

```
[
    {
        "fields": {
            "as_ids": [
                "150.0@s",
                "120.0@i",
                "121.0@i",
                "126.0@i"
            ],
            "i_input": 1,
            "i_slot": 8,
            "s_card_label": "7880DM-ATSC",
            "s_frame_label": "Super Frame",
            "s_card_type": "7880DM4-ATSC",
            "s_input_tag": "KTWO (ASI / OTA)",
            "s_input_status": "Not Locked",
            "i_input_power": -80,
            "i_input_mer": 0
        },
        "host": "172.16.185.22",
        "name": "rf_demod"
    },
    {
        "fields": {
            "as_ids": [
                "150.1@s",
                "120.1@i",
                "121.1@i",
                "126.1@i"
            ],
            "i_input": 2,
            "i_slot": 8,
            "s_card_label": "7880DM-ATSC",
            "s_frame_label": "Super Frame",
            "s_card_type": "7880DM4-ATSC",
            "s_input_tag": "KGWC (ASI / OTA)",
            "s_input_status": "Not Locked",
            "i_input_power": -80,
            "i_input_mer": 0
        },
        "host": "172.16.185.22",
        "name": "rf_demod"
    },
    {
        "fields": {
            "as_ids": [
                "150.2@s",
                "120.2@i",
                "121.2@i",
                "126.2@i"
            ],
            "i_input": 3,
            "i_slot": 8,
            "s_card_label": "7880DM-ATSC",
            "s_frame_label": "Super Frame",
            "s_card_type": "7880DM4-ATSC",
            "s_input_tag": "KCWY / KCWY2 (OTA)",
            "s_input_status": "Not Locked",
            "i_input_power": -80,
            "i_input_mer": 0
        },
        "host": "172.16.185.22",
        "name": "rf_demod"
    },
    {
        "fields": {
            "as_ids": [
                "150.3@s",
                "120.3@i",
                "121.3@i",
                "126.3@i"
            ],
            "i_input": 4,
            "i_slot": 8,
            "s_card_label": "7880DM-ATSC",
            "s_frame_label": "Super Frame",
            "s_card_type": "7880DM4-ATSC",
            "s_input_tag": "",
            "s_input_status": "Not Locked",
            "i_input_power": -80,
            "i_input_mer": 0
        },
        "host": "172.16.185.22",
        "name": "rf_demod"
    },
    {
        "fields": {
            "as_ids": [
                "150.0@s",
                "120.0@i",
                "121.0@i",
                "126.0@i"
            ],
            "i_input": 1,
            "i_slot": 15,
            "s_card_label": "Crazy Card",
            "s_frame_label": "Super Frame",
            "s_card_type": "7880DM4-ATSC",
            "s_input_tag": "RF1",
            "s_input_status": "Locked",
            "i_input_power": -52,
            "i_input_mer": 29
        },
        "host": "172.16.185.22",
        "name": "rf_demod"
    },
    {
        "fields": {
            "as_ids": [
                "150.1@s",
                "120.1@i",
                "121.1@i",
                "126.1@i"
            ],
            "i_input": 2,
            "i_slot": 15,
            "s_card_label": "Crazy Card",
            "s_frame_label": "Super Frame",
            "s_card_type": "7880DM4-ATSC",
            "s_input_tag": "tom",
            "s_input_status": "Locked",
            "i_input_power": -58,
            "i_input_mer": 25
        },
        "host": "172.16.185.22",
        "name": "rf_demod"
    },
    {
        "fields": {
            "as_ids": [
                "150.2@s",
                "120.2@i",
                "121.2@i",
                "126.2@i"
            ],
            "i_input": 3,
            "i_slot": 15,
            "s_card_label": "Crazy Card",
            "s_frame_label": "Super Frame",
            "s_card_type": "7880DM4-ATSC",
            "s_input_tag": "super input",
            "s_input_status": "Locked",
            "i_input_power": -58,
            "i_input_mer": 26
        },
        "host": "172.16.185.22",
        "name": "rf_demod"
    },
    {
        "fields": {
            "as_ids": [
                "150.3@s",
                "120.3@i",
                "121.3@i",
                "126.3@i"
            ],
            "i_input": 4,
            "i_slot": 15,
            "s_card_label": "Crazy Card",
            "s_frame_label": "Super Frame",
            "s_card_type": "7880DM4-ATSC",
            "s_input_tag": "nothing",
            "s_input_status": "Locked",
            "i_input_power": -53,
            "i_input_mer": 29
        },
        "host": "172.16.185.22",
        "name": "rf_demod"
    }
]
```
