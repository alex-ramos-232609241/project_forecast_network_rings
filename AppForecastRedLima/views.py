import threading
import copy
from dataclasses import dataclass, field
from typing import List
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from AppForecastRedLima.models import InfoEnlace, InfoForecast
from AppForecastRedLima.serializers import InfoEnlaceSerializer
from AppForecastRedLima.composite import CompositeRing, Link, Aggregator
from AppForecastRedLima.services import delete_forecast_database, call_main_database, get_forecast_database
from AppForecastRedLima.services import ThreadAppForecast
from datetime import datetime

from coloreando import *

event = threading.Event()

@dataclass
class MainEngine:
    list_rings_all: List = field(default_factory=list)

    def update_list_data_rings(self, new_list: List) -> None:
        self.list_rings_all = new_list
       
    
object_main = MainEngine()
lima_network = CompositeRing('RedLima')
network_structure = {}

from datetime import datetime

def update_rings(date=None, percentile=None):
    request_date = datetime.strptime(date, '%Y-%m-%d').date() if date else datetime.now().date()
    
    data_rings = call_main_database(request_date=request_date, choice=percentile)
    
    object_main.update_list_data_rings(data_rings)
    create_structure_composite(object_main.list_rings_all)


ThreadAppForecast(update_rings, event, 30000)

class InfoView(APIView): 
    def get(self, request, format=None):
        data_de_info = InfoEnlace.objects.all()[:10]
        data_de_info_serializer = InfoEnlaceSerializer(data_de_info, many=True)

        return Response(data_de_info_serializer.data, status=status.HTTP_200_OK)

def create_structure_composite(l):
    if lima_network._children != []:
        lima_network._children.clear()
        network_structure.clear()
    for k in l:
        network_structure[f"object{k}"] = CompositeRing([k])
        lima_network.add(network_structure[f"object{k}"])
        for v in l[k][:len(l[k]) - 1]:
            network_structure[f"object{v[0]}"] = Link(v)
            network_structure[f"object{k}"].add(network_structure[f"object{v[0]}"])

        for u in l[k][len(l[k]) - 1:]:
            for x in u:
                network_structure[f"object{x[0]}"] = Aggregator(list(x))
                network_structure[f"object{k}"].add(network_structure[f"object{x[0]}"])

        network_structure[f"case_{k}"] = CompositeRing([f"case_{k}"])
        network_structure[f"object{k}"].add(network_structure[f"case_{k}"])
        network_structure[f"fall_1_link"] = CompositeRing(["fall_1_link"])
        network_structure[f"case_{k}"].add(network_structure[f"fall_1_link"])
        create_list_one_fall(k1=k, L1=l, network_structure=network_structure)

        network_structure[f"fall_2_link"] = CompositeRing(["fall_2_link"])
        network_structure[f"case_{k}"].add(network_structure[f"fall_2_link"])
        
        create_list_two_fall(k2=k, L2=l, network_structure=network_structure)



def create_list_one_fall(k1, l1, network_structure) -> list:
    pass

def create_list_two_fall(k2, l2, network_structure) -> list:
    pass

class InfoRings(APIView):
    
    def get(self, request, format=None): 
        try:
            total_data = lima_network.data_generate_api()
            return Response({"data": total_data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DataRingNorth1(APIView):
   
    def get(self, request, format=None):
        try:
            north_ring_data = network_structure["object_ring_north1"].data_generate_api()
            return Response(north_ring_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DataRingEast(APIView):

    def get(self, request, format=None):
        try:
            east_ring_data = network_structure["object_ring_east"].data_generate_api()
            return Response(east_ring_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DataRingNorth2(APIView):

    def get(self, request, format=None):
        try:
            north2_ring_data = network_structure["object_ring_north2"].data_generate_api()
            return Response(north2_ring_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DataRingSouth(APIView):

    def get(self, request, format=None):
        try:
            south_ring_data = network_structure["object_ring_south"].data_generate_api()
            return Response(south_ring_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DataRingWest(APIView):

    def get(self, request, format=None):
        try:
            west_ring_data = network_structure["object_ring_west"].data_generate_api()
            return Response(west_ring_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateGeneralList(APIView):
    def get(self, request, format=None, date=None):
        response_message = ""
        
        try:
            update_rings(date=date, percentile=None)
            response_message = "Successfully updated general list"
            return Response({"message": response_message}, status=status.HTTP_200_OK)
            
        except Exception as e:
            response_message = "Something went wrong"
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateGeneralListPercentile(APIView):
    def get(self, request, format=None, percentile=None):
        response_message = ""
        
        try:
            update_rings(date=None, percentile=percentile)
            response_message = "Successfully updated general list with percentile"
            return Response({"message": response_message}, status=status.HTTP_200_OK)
            
        except Exception as e:
            response_message = "Something went wrong"
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class DataForecast(APIView):
    def get(self, request, format=None):
        try:
            values = get_forecast_database(self)
            return Response(values.values(), status=status.HTTP_200_OK)
        except:
            return Response({"Error"}, status=status.HTTP_400_BAD_REQUEST)
            
    def post(self, request, format=None):
        if request.data:
            try:
                for x in request.data:
                    if InfoForecast(date=x['date'], forecast_value=x['forecast']):
                        pass
                    else: 
                        break    
                delete_forecast_database(self)
                for d in request.data:
                    forecast_info = InfoForecast(date=d['date'], forecast_value=d['forecast'])
                    forecast_info.save()
                text_send = "Successful send"
            except:
                text_send = "Error, unable to upload file"   
        else:
            text_send = "You must send the forecast file"
        return Response({text_send}, status=status.HTTP_200_OK)


class TopTenLinksByTraffic(APIView):
    def get(self, request, format=None):
        try:
            link_ring_list = object_main.list_rings_all
            sort_list = []
            
            for ring_link in link_ring_list:
                for v in copy.deepcopy(link_ring_list[ring_link][:len(link_ring_list[ring_link])-1]):
                    v.append((v[6] / 100000000) / (v[7] / 1000) * 100)
                    t = tuple(v)
                    sort_list.append(t)
            
            sorted_list = sorted(sort_list, key=lambda value: value[9], reverse=True)
            sorted_list = sorted_list[:10]
            return Response(sorted_list, status=status.HTTP_200_OK)
        except:
            e = 'An error occurred'
            return Response({e}, status=status.HTTP_404_NOT_FOUND)


class UpdatePortCapacity(APIView):
    def post(self, request, format=None):
        if request.data:
            try:
                link_id = request.data['cid']
                port_capacity = request.data['port_capacity'] * 1000

                InfoEnlace.objects.filter(id=link_id).update(port_capacity=port_capacity)
                msg_send = "Update Successful"
                s = status.HTTP_200_OK 
            except:
                msg_send = "Error, Update could not be performed"
                s = status.HTTP_304_NOT_MODIFIED
        else:
            msg_send = "No data to update"
            s = status.HTTP_204_NO_CONTENT    
        return Response({'msg_send': msg_send}, status=s)


class TopTenLinksAboutToSaturateDoubleFall(APIView):
    def get(self, request):
        components = "Components"
        val_north1 = network_structure["object_ring_north1"].data_generate_api()
        val_east = network_structure["object_ring_east"].data_generate_api()
        val_north2 = network_structure["object_ring_north2"].data_generate_api()
        val_south = network_structure["object_ring_south"].data_generate_api()
        val_west = network_structure["object_ring_west"].data_generate_api()

        
        ring_list = [val_north1, val_east, val_north2, val_south, val_west]
        unsorted_list = []
        repeated_values_list = []
        
        for ring in ring_list:
            relative_values = []
            repeated_values = []
            
            for k in ring[components][len(ring[components]) - 1][components][1][components]:
                links_to_saturate_in_scenario = [] 
                affected_links = []
                
                for i in k[components]:
                    scenario_in_scenario = []
                    capacity = i['port_capacity'] / 1000
                    
                    if i['utilization'] < 0:
                        affected_links.append(i['link_db'])
                    
                    my_list = []    
                    for j in i['forecast']:
                        if j['forecast_value'] > capacity:
                            forecast_date = j['date']
                            for v in i['forecast']:
                                if v['date'].year == forecast_date.year:
                                    my_list.append(v['forecast_value'])     
                            maximum = max(my_list)
                            
                            scenario_in_scenario.append(k["name"])
                            scenario_in_scenario.append(i['cid'])
                            scenario_in_scenario.append(i['link_db'])
                            scenario_in_scenario.append(j['date'])
                            scenario_in_scenario.append(capacity)
                            scenario_in_scenario.append(j['forecast_value'])
                            scenario_in_scenario.append(maximum)
                            break
                    links_to_saturate_in_scenario.append(scenario_in_scenario)
                links_to_saturate_in_scenario.append(affected_links)
                relative_values.append(links_to_saturate_in_scenario)
            
            for vr in relative_values:
                for i in vr:
                    if i != vr[len(vr) - 1]: 
                        i.append(vr[len(vr) - 1])
                vr.pop(len(vr) - 1)
            
            initial_values = copy.deepcopy(relative_values[0])
            
            for vi in relative_values:
                if vi != relative_values[0]:
                    for m, n in zip(vi, initial_values):
                        if len(m) != 1 and len(n) != 1:
                            if m[3] < n[3]:
                                index = vi.index(m)
                                initial_values[index] = m
                            if m[3] == n[3]:
                                repeated_values.append(m)  
                        elif len(m) != 1 and len(n) == 1:
                            ind = vi.index(m)
                            initial_values[ind] = m   

            for x in initial_values:
                if len(x) > 1:
                    unsorted_list.append(x)
            for y in repeated_values:
                if len(y) > 1:
                    repeated_values_list.append(y)

        sorted_list = sorted(unsorted_list, key=lambda val: val[3])

        sorted_repeated_values = sorted(sorted_list, key=lambda val : val[3])
        return Response({'topTenLinksAboutToSaturate': sorted_list, 'RepeatedValuesList': sorted_repeated_values}, status=status.HTTP_200_OK)
