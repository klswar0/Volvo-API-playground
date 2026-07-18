import asyncio
from typing import Dict, Set

#TODO: trigger update with more than one attribute at a time. (for scenarios)
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
                
    def update_packet(self, vin: str, car_instance, changed_attribute: str):
        update_packet = {
                "VIN": vin,
                "attribute_name": changed_attribute,
                "current_value": getattr(car_instance, changed_attribute),
            }
        return update_packet

    def trigger_update(self, vin: str, car_instance, changed_attribute: str):
        """Call this function whenever a car's data changes in your database."""
        if vin in self._subscribers:    
            update_packet = self.update_packet(vin, car_instance, changed_attribute)
            for queue in self._subscribers[vin]:
                queue.put_nowait(update_packet)
    #NOTE: This implementation is made to minimize code changes and should be CHANGED in the future
    # should be changed to a more efficient implementation sending in one packet
    def trigger_update_multiple(self, vin: str, car_instance, changed_attributes: list):
        """Call this func when more than one attribute changes in the car."""
        if vin in self._subscribers:
            for changed_attribute in changed_attributes:
                update_packet = self.update_packet(vin, car_instance, changed_attribute)
                for queue in self._subscribers[vin]:
                    queue.put_nowait(update_packet)

        
notifier = websocketNotifier()