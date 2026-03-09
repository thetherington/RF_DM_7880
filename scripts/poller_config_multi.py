import json

from dm_atsc_collector import (
    DMCollectorMultiFrame,
    DMCollectorParams,
    frame_to_documents,
)
from insite_plugin import InsitePlugin


class Plugin(InsitePlugin):
    def can_group(self):
        return True

    def fetch(self, hosts):
        try:

            self.collector

        except Exception:

            params: DMCollectorParams = {
                "ip": "localhost",
                "slots": [],
                "nms": {"server": "nms-server-ip", "version": "vistalink"},
                "legacy": False,
            }

            self.collector = DMCollectorMultiFrame(hosts, **params)

        frame = self.collector.run()

        documents = []

        for host, frame in frame.items():
            documents.extend(frame_to_documents(host, frame))

        return json.dumps(documents)
