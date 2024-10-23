import abc
from typing import List
from AppForecastRedLima.servicios import *


class Component(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def data_generate_api(self) -> dict:
        pass

class Enlace(Component):
    lista_enlaces = []

    def __init__(self, lista_enlaces):
        self.lista_enlaces = lista_enlaces

    def data_generate_api(self) -> dict:
        data_forecast = traer_forecast_de_basedatos(self)
        lista_nueva1 = []
        for v in data_forecast.values():
            lista_nueva1.append(list((v['Fecha'],v['Fecha'].year, v['Fecha'].month, v['Fecha'].day,v['Forecast_valor'])))
        listaForecast1 = obtener_forecast(lista=self.lista_enlaces, listaForecast=lista_nueva1)
        return {
            "enlace": self.lista_enlaces[0],
            "medioDeTransmision": self.lista_enlaces[1],
            "cid": self.lista_enlaces[2],
            "enlace de DB": self.lista_enlaces[3],
            "equipo1": self.lista_enlaces[4],
            "capacidad_puerto": self.lista_enlaces[5],
            "utilizacion": self.lista_enlaces[6]/100000000,
            "capacidad" : self.lista_enlaces[7],
            "fecha": self.lista_enlaces[8],
            "forecast": listaForecast1 
        }

    

class Agregador(Component):
    lista_agregador = []
    def __init__(self,lista_agregador):
       self.lista_agregador = lista_agregador
       

    def data_generate_api(self) -> dict:
        data_forecast = traer_forecast_de_basedatos(self)
        lista_nueva2 = []
        for v in data_forecast.values():
            lista_nueva2.append(list((v['Fecha'],v['Fecha'].year, v['Fecha'].month, v['Fecha'].day,v['Forecast_valor'])))
        listaForecast2 = obtener_rorecast_agregadores(lista=self.lista_agregador,listaForecast=lista_nueva2)
        
        return {
            "agregador": self.lista_agregador[0],
            "utilizacion": self.lista_agregador[1],
            "forecast": listaForecast2
        }

  
class CompositeAnillo(Component):
    nombre = []

    def __init__(self, nombre) -> None:
        self.nombre = nombre
        self._children: List[Component] = []

    def add(self, component : Component) -> None:
        self._children.append(component)
        component.parent = self

    def remove(self, component: Component) -> None:
        self._children.remove(component)
        component.parent = None

    def is_composite(self) -> bool:
        return True    
 

    def data_generate_api(self) -> dict:
        listaTotal = []
        if self.nombre == "RedLima":
            nom = "Anillos"
        else:
            nom = "Componentes"
        for child in self._children:
            listaTotal.append(child.data_generate_api())
        return {"nombre": self.nombre,
                f"{nom}" : listaTotal}
