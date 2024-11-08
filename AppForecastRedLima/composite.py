import abc
from dataclasses import dataclass, field
from typing import List, Dict
from AppForecastRedLima.services import *


class Component(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def data_generate_api(self) -> Dict[str, any]:
        pass

@dataclass
class Link(Component):
    link_list: List

    def data_generate_api(self) -> Dict[str, any]:
        data_forecast = get_forecast_database(self)

        forecast_list = [
            [value['Fecha'], value['Fecha'].year, value['Fecha'].month, value['Fecha'].day, value['Forecast_valor']]
            for value in data_forecast.values()
        ]
        forecast = get_forecast(list=self.link_list, forecast_list=forecast_list)

        link, transmission_medium, cid, link_db, equipment, port_capacity, utilization, capacity, data = self.link_list
        return {
            "link": link,
            "transmission_medium": transmission_medium,
            "cid": cid,
            "link_db": link_db,
            "equipment": equipment,
            "port_capacity": port_capacity,
            "utilization": utilization/100_000_000,
            "capacity" : capacity,
            "data": data,
            "forecast": forecast 
        }

    

@dataclass
class Aggregator:
    aggregator_list: List

    def data_generate_api(self) -> Dict[str, Any]:

        data_forecast = get_forecast_database(self)
        
        forecast_data = [
            [v['Fecha'], v['Fecha'].year, v['Fecha'].month, v['Fecha'].day, v['Forecast_valor']]
            for v in data_forecast.values()
        ]

        forecast = get_forecast_aggregators(list=self.aggregator_list, forecast_list=forecast_data)

        aggregator, utilization = self.aggregator_list    

        return {
            "aggregator": aggregator,
            "utilization": utilization,
            "forecast": forecast
        }


@dataclass
class CompositeRing:
    name: str
    _children: List[Component] = field(default_factory=list)

    def add(self, component: Component) -> None:
        self._children.append(component)
        component.parent = self

    def remove(self, component: Component) -> None:
        self._children.remove(component)
        component.parent = None

    def is_composite(self) -> bool:
        return True    

    def data_generate_api(self) -> Dict[str, any]:
        group_name = "Anillos" if self.name == "RedLima" else "Componentes"
        
        children_data = [child.data_generate_api() for child in self._children]
        
        return {
            "name": self.name,
            group_name: children_data
        }