import asyncio
from typing import Dict, Set


class websocketNotifier:
    def __init__(self):
        self._subscribers: Dict[str, Set[asyncio.Queue]] = {}
    def subscribe(self, vin: str) -> asyncio.Queue:
        queue = asyncio.Queue()
        self._subscribers.setdefault(vin, set()).add(queue)
        return queue

    def unsubscribe(self, vin: str, queue: asyncio.Queue):
        if vin in self._subscribers:
            self._subscribers[vin].discard(queue)
            if not self._subscribers[vin]:
                del self._subscribers[vin]

    def trigger_update(self, vin: str, car_instance, changed_attribute: str):
        """Call this function whenever a car's data changes in your database."""
        if vin in self._subscribers:    
            update_packet = {
                "VIN": vin,
                "attribute_name": changed_attribute,
                "current_value": getattr(car_instance, changed_attribute),
            }
            for queue in self._subscribers[vin]:
                queue.put_nowait(update_packet)
        
notifier = websocketNotifier()