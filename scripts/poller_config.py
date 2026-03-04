import json

from dm_atsc_collector import DMCollector, DMCollectorParams
from insite_plugin import InsitePlugin


class Plugin(InsitePlugin):
    def can_group(self):
        return False

    def fetch(self, hosts):

        host = hosts[-1]

        try:

            self.collector

        except Exception:

            params: DMCollectorParams = {
                "ip": host,
                "slots": [],
                "nms": {"server": "nms-server-ip", "version": "vistalink"},
            }

            self.collector = DMCollector.auto_discover("7880DM4-ATSC", **params)

        frame = self.collector.run()

        documents = []

        for _, card in frame.items():
            if card is None or not isinstance(card, dict):
                continue

            for _, instance in card.items():
                document = {
                    "fields": instance,
                    "host": host,
                    "name": "rf_demod",
                }

                documents.append(document)

        return json.dumps(documents)
