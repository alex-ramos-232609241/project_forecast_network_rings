import threading
import copy
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from AppForecastRedLima.models import InfoEnlace, InfoForecast
from AppForecastRedLima.serializers import InfoEnlaceSerializer
from AppForecastRedLima.composite import CompositeAnillo,Enlace,Agregador
from AppForecastRedLima.servicios import eliminar_forecast_de_basedatos, llamada_principal_basedatos,traer_forecast_de_basedatos
from AppForecastRedLima.servicios import ThreadAppForecast
from datetime import datetime

from coloreando import *

event = threading.Event()

class MotorPrincipal():
    
    lista_anillos_totales = []

    def update_list_data_rings(self,l):
        self.lista_anillos_totales = l
       
    
objeto_principal = MotorPrincipal()
red_lima = CompositeAnillo('RedLima')
mydic = {}

def ejecutar_manualmente(f):
    
    f = datetime.strptime(f,'%Y-%m-%d').date()
    dAnillos = llamada_principal_basedatos(fechaDePeticion=f)
    objeto_principal.update_list_data_rings(dAnillos)
    crear_estructura_composite(objeto_principal.lista_anillos_totales)

def ejecutar_cierto_tiempo(percentil=None):
    dAnillos = llamada_principal_basedatos(fechaDePeticion=datetime.now().date(), eleccion=percentil)
    objeto_principal.update_list_data_rings(dAnillos)
    crear_estructura_composite(objeto_principal.lista_anillos_totales)

kevent = ThreadAppForecast(ejecutar_cierto_tiempo, event, 30000)

class InfoView(APIView): 
    def get(self, request, format=None):
        data_de_info = InfoEnlace.objects.all()[:10]
        data_de_info_serializer = InfoEnlaceSerializer(data_de_info, many=True)

        return Response(data_de_info_serializer.data, status=status.HTTP_200_OK)

def crear_estructura_composite(l):
    if red_lima._children != []:
        red_lima._children.clear()
        mydic.clear()
    for k in l:
        mydic[f"objeto{k}"] = CompositeAnillo([k])
        red_lima.add(mydic[f"objeto{k}"])
        for v in l[k][:len(l[k]) - 1]:
            mydic[f"objeto{v[0]}"] = Enlace(v)
            mydic[f"objeto{k}"].add(mydic[f"objeto{v[0]}"])

        for u in l[k][len(l[k]) - 1:]:
            for x in u:
                mydic[f"objeto{x[0]}"] = Agregador(list(x))
                mydic[f"objeto{k}"].add(mydic[f"objeto{x[0]}"])

        mydic[f"casos_{k}"] = CompositeAnillo([f"casos_{k}"])
        mydic[f"objeto{k}"].add(mydic[f"casos_{k}"])
        mydic[f"caida_1_enlace"] = CompositeAnillo(["caida_1_enlace"])
        mydic[f"casos_{k}"].add(mydic[f"caida_1_enlace"])
        # algoritmo de 1 caida
        creando_listas_una_caida(k1=k, L1=l, mdic1=mydic)

        mydic[f"caida_2_enlaces"] = CompositeAnillo(["caida_2_enlaces"])
        mydic[f"casos_{k}"].add(mydic[f"caida_2_enlaces"])
        # algoritmo de 2 caida
        creando_listas_dos_caidas(k2=k, L2=l, mdic2=mydic)



def creando_listas_una_caida(k1, l1, mdic1) -> list:
    i = 0
    lista_agradores_por_anillo = copy.deepcopy(l1[k1][len(l1[k1])-1:][0])  # agregadores
    """
    [
        ['MOLINA', 3.7800309999999975],
        ['E.CUADRO', 4.024064540000001],
        ['HUACHIPA', 26.7908778],
        ['N.LURIGANCHO', 3.5452154900000004],
        ['MILLA', 9.08172335]
    ]
    """
    li_enlaces_x_a = copy.deepcopy(l1[k1][:len(l1[k1])-1])  # anillos
    """
    [
        ['Molina-SBO', 'DWDM', 6599, 'Bundle_Molina_to_SBO_Este_Entel_DWDM', 'LIM_MLNA_AGG_2', 'LIM_SBRJ_P_2', 2369551760, 40000, datetime.date(2021, 5, 19)],
        ['Molina-E.Cuadro', 'DWDM', 6609, 'Bundle_Molina_to_E.Cuadro_Este_Entel_DWDM', 'LIM_ECDR_AGG_1', 'LIM_MLNA_AGG_2', 1991548660, 40000, datetime.date(2021, 5, 19)],
        ['E.Cuadro-Huachipa', 'FO', 6619, 'Bundle_E.Cuadro_to_Huachipa_Este_Entel_FO', 'LIM_ECDR_AGG_1', 'LIM_HCHP_AGG_1', 1589142206, 30000, datetime.date(2021, 5, 19)],
        ['Huachipa-N.lurigancho', 'DWDM', 6629, 'Bundle_Huachipa_to_N.lurigancho_Este_Entel_DWDM', 'LIM_HCHP_AGG_1', 'LIM_NLUR_AGG_1 ', 1089945574, 30000, datetime.date(2021, 5, 19)],
        ['N.Lurigancho-Milla', 'DWDM', 6639, 'Bundle_N.Lurigancho_to_Milla_Este_Entel_DWDM', 'LIM_LAMI_AGG_1', 'LIM_NLUR_AGG_1', 1444467123, 30000, datetime.date(2021, 5, 19)],
        ['Milla-MIR', 'DWDM', 6649, 'Bundle_Milla_to_MIR_Este_Entel_DWDM', 'LIM_LAMI_AGG_1', 'LIM_MIRA_P_2', 2352639458, 40000, datetime.date(2021, 5, 19)],
        ['Milla-Molina', 'DWDM', 6679, 'Bundle_Milla_to_Molina_Este_Entel_DWDM', 'LIM_LAMI_AGG_1', 'LIM_MLNA_AGG_2', 207059, 40000, datetime.date(2021, 5, 19)]
    ]
    """

    for m in l1[k1][:len(l1[k1])-1]:
        acum = 0
        for agre in lista_agradores_por_anillo:
            suma_total_gregadores = agre[1] + acum
            acum = acum + agre[1]
        mdic1[f"enlace_afectado_{m[0]}"] = CompositeAnillo([f"enlace_afectado_{m[0]}"])
        mdic1[f"caida_1_enlace"].add(mdic1[f"enlace_afectado_{m[0]}"])
        
        if i == 0:
            lista_valores = [-1, lista_agradores_por_anillo[1][1], 0, lista_agradores_por_anillo[2][1], lista_agradores_por_anillo[2][1] + lista_agradores_por_anillo[3][1], suma_total_gregadores, lista_agradores_por_anillo[0][1] + lista_agradores_por_anillo[1][1]]
            j = 0
            if len(lista_agradores_por_anillo) == 4:
                lista_valores.pop(4)

            for li_e in copy.deepcopy(li_enlaces_x_a):
                li_e[6] = lista_valores[j] * 100000000
                enlace_nuevo = li_e    
                j = j + 1
                mdic1[f"enlace_con_caida_de_{li_e[0]}"] = Enlace(enlace_nuevo)
                mdic1[f"enlace_afectado_{m[0]}"].add(mdic1[f"enlace_con_caida_de_{li_e[0]}"])
        elif i > 0 and i < len(lista_agradores_por_anillo):
            suma_acumlada1 = 0
            suma_acumlada2 = 0
            lista_de_valores_para_enlaces_nuevos = []
            
            for l_a1 in lista_agradores_por_anillo[:i]:
                semi_suma_total1 = l_a1[1] + suma_acumlada1
                suma_acumlada1 = suma_acumlada1 + l_a1[1]
            lista_de_valores_para_enlaces_nuevos.append(semi_suma_total1)  
            for l_a1 in lista_agradores_por_anillo[:i-1]:
                nueva_semi_suma1 = semi_suma_total1 - l_a1[1]
                semi_suma_total1 = nueva_semi_suma1
                lista_de_valores_para_enlaces_nuevos.append(nueva_semi_suma1)
            lista_de_valores_para_enlaces_nuevos.append(-1)            
            for l_a2 in lista_agradores_por_anillo[i:]:
                semi_suma_total2 = l_a2[1] + suma_acumlada2
                suma_acumlada2 = suma_acumlada2 + l_a2[1]
                lista_de_valores_para_enlaces_nuevos.append(semi_suma_total2)
            lista_de_valores_para_enlaces_nuevos.append(0)      
            j = 0
            for li_e1 in copy.deepcopy(li_enlaces_x_a):
                li_e1[6] = lista_de_valores_para_enlaces_nuevos[j] * 100000000
                enlace_nuevo = li_e1    
                j = j + 1
                mdic1[f"enlace_con_caida_de_{li_e1[0]}"] = Enlace(enlace_nuevo)
                mdic1[f"enlace_afectado_{m[0]}"].add(mdic1[f"enlace_con_caida_de_{li_e1[0]}"])   
        elif i == len(lista_agradores_por_anillo):
            if i == 4:
                lista_generar_enlaces = [suma_total_gregadores, lista_agradores_por_anillo[1][1], 0, lista_agradores_por_anillo[2][1], -1, lista_agradores_por_anillo[2][1] + lista_agradores_por_anillo[3][1]]
            elif i == 5:
                lista_generar_enlaces = [suma_total_gregadores, lista_agradores_por_anillo[1][1] + lista_agradores_por_anillo[2][1], lista_agradores_por_anillo[2][1], 0, lista_agradores_por_anillo[3][1], -1, lista_agradores_por_anillo[3][1] + lista_agradores_por_anillo[4][1]] 
            j = 0
            for li_e2 in copy.deepcopy(li_enlaces_x_a):
                li_e2[6] = lista_generar_enlaces[j] * 100000000
                nuevo_enlace = li_e2
                j = j + 1
                mdic1[f"enlace_con_caida_de_{li_e2[0]}"] = Enlace(nuevo_enlace)
                mdic1[f"enlace_afectado_{m[0]}"].add(mdic1[f"enlace_con_caida_de_{li_e2[0]}"])  
        elif i > len(lista_agradores_por_anillo):
            pass
        
        i = i + 1
    

def creando_listas_dos_caidas(k2, l2, mdic2) -> list:
    """Copia la lista de agregadores"""
    pass
     


class InfoAnillos(APIView):
    
    def get(self, request, format=None): 
        try:
            totales = red_lima.data_generate_api()
        except:
            totales = []
        return Response(totales, status=status.HTTP_200_OK)

class DataAnilloNorte1(APIView):
   
    def get(self, request, format=None):
        try:
            d_an1 = mydic["objeto_anillo_norte1"].data_generate_api()
        except:
            d_an1 = [] 
        return Response(d_an1, status=status.HTTP_200_OK)

class DataAnilloEste(APIView):

    def get(self, request, format=None):
        try:
            d_ae = mydic["objeto_anillo_este"].data_generate_api()
        except:
            d_ae = []
        return Response(d_ae, status=status.HTTP_200_OK)

class DataAnilloNorte2(APIView):

    def get(self, request, format=None):
        try:
            d_an2 = mydic["objeto_anillo_norte2"].data_generate_api()
        except:
            d_an2 = []   
        return Response(d_an2, status=status.HTTP_200_OK)

class DataAnilloSur(APIView):

    def get(self, request, format=None):
        try:
            d_as = mydic["objeto_anillo_sur"].data_generate_api()
        except:
            d_as = [] 
        return Response(d_as, status=status.HTTP_200_OK)

class DataAnilloOeste(APIView):

    def get(self, request, format=None):
        try:
            d_ao = mydic["objeto_anillo_oeste"].data_generate_api()
        except:
            d_ao = [] 
        return Response(d_ao, status=status.HTTP_200_OK)

class ActualizarListaGeneral(APIView):
    def get(self, request, format=None, fecha=None):
        mostrar = ""
        
        try:
            if fecha is None:
                ejecutar_cierto_tiempo()
            else:    
                ejecutar_manualmente(f=fecha)
            mostrar = "Éxito"
            
        except:
            mostrar = "Algo salió mal"
            
        return Response(mostrar, status=status.HTTP_200_OK)

class ActualizarListaGeneralPercentil(APIView):
    def get(self, request, format=None, percentil=None):
        mostrar = ""
        
        try:
            if percentil == 'percentil':
                ejecutar_cierto_tiempo(percentil)
            mostrar = "Éxito"
            
        except:
            mostrar = "Algo salió mal"
            
        return Response(mostrar, status=status.HTTP_200_OK)

class DataForecast(APIView):
    def get(self, request, format=None):
        try:    
            valores = traer_forecast_de_basedatos(self)
            return Response(valores.values(), status=status.HTTP_200_OK)
        except:
            return Response({"Error"}, status=status.HTTP_400_BAD_REQUEST)
            
    def post(self, request, format=None):
        if request.data:
            try:
                for x in request.data:
                    if InfoForecast(fecha=x['fecha'], forecast_valor=x['forecast']):
                        pass
                    else: 
                        break    
                eliminar_forecast_de_basedatos(self)
                for d in request.data:
                    info_f = InfoForecast(fecha=d['fecha'], forecast_valor=d['forecast'])
                    info_f.save()
                text_envio = "Envío exitoso"
            except:
                text_envio = "Error, No se pudo cargar archivo"   
        else:
            text_envio = "Debe enviar el archivo de forecast"
        return Response({text_envio}, status=status.HTTP_200_OK)

class TopTenEnlacesMayorTrafico(APIView):
    def get(self, request, format=None):
        try:
            lista_enlace_por_anillo = objeto_principal.lista_anillos_totales
            lista_para_ordenamiento = []
            
            for enlace_por_anillo in lista_enlace_por_anillo:
                for v in copy.deepcopy(lista_enlace_por_anillo[enlace_por_anillo][:len(lista_enlace_por_anillo[enlace_por_anillo])-1]):
                    v.append((v[6] / 100000000) / (v[7] / 1000) * 100)
                    t = tuple(v)
                    lista_para_ordenamiento.append(t)
            
            lista_ordenada = sorted(lista_para_ordenamiento, key=lambda value: value[9], reverse=True)
            lista_ordenada = lista_ordenada[:10]
            return Response(lista_ordenada, status=status.HTTP_200_OK)
        except:
            e = 'Ocurrió un error'
            return Response({e}, status=status.HTTP_404_NOT_FOUND)

class UpdateCapacidadPuerto(APIView):
    def post(self, request, format=None):
        if request.data:
            try:
                id_enlace = request.data['cid']
                capacidad_puerto = request.data['capacidad_puerto'] * 1000

                InfoEnlace.objects.filter(id=id_enlace).update(capacidad_puerto=capacidad_puerto)
                msg_enviar = "Actualización Exitosa"
                s = status.HTTP_200_OK 
            except:
                msg_enviar = "Error, No se pudo realizar la actualización"
                s = status.HTTP_304_NOT_MODIFIED
        else:
            msg_enviar = "No hay datos de actualizar"
            s = status.HTTP_204_NO_CONTENT    
        return Response({'msg_enviar': msg_enviar}, status=s)

class TopTenEnlacesProximosSaturarDobleCaida(APIView):
    def get(self, request):
        cpmts = "Componentes"
        val_a_norte1 = mydic["objeto_anillo_norte1"].data_generate_api()
        val_a_este = mydic["objeto_anillo_este"].data_generate_api()
        val_a_norte2 = mydic["objeto_anillo_norte2"].data_generate_api()
        val_a_sur = mydic["objeto_anillo_sur"].data_generate_api()
        val_a_oeste = mydic["objeto_anillo_oeste"].data_generate_api()
        
        lista_anillos = [val_a_norte1, val_a_este, val_a_norte2, val_a_sur, val_a_oeste]
        lista_sin_ordenar = []
        lista_de_valores_repetidos = []
        
        for lista_ani in lista_anillos:
            valores_relativos = []
            val_repetidos = []
            
            for k in lista_ani[cpmts][len(lista_ani[cpmts]) - 1][cpmts][1][cpmts]:
                enlaces_a_saturar_en_escenario = [] 
                enlaces_afectados = []
                
                for i in k[cpmts]:
                    en_s_escenario = []
                    c = i['capacidad_puerto'] / 1000
                    
                    if i['utilizacion'] < 0:
                        enlaces_afectados.append(i['enlace de db'])
                    
                    my_lista = []    
                    for j in i['forecast']:
                        if j['valor_forecast'] > c:
                            fe = j['fecha']
                            for v in i['forecast']:
                                if v['fecha'].year == fe.year:
                                    my_lista.append(v['valor_forecast'])     
                            maximo = max(my_lista)
                            
                            en_s_escenario.append(k["nombre"])
                            en_s_escenario.append(i['cid'])
                            en_s_escenario.append(i['enlace de db'])
                            en_s_escenario.append(j['fecha'])
                            en_s_escenario.append(c)
                            en_s_escenario.append(j['valor_forecast'])
                            en_s_escenario.append(maximo)
                            break
                    enlaces_a_saturar_en_escenario.append(en_s_escenario)
                enlaces_a_saturar_en_escenario.append(enlaces_afectados)
                valores_relativos.append(enlaces_a_saturar_en_escenario)
            
            for vr in valores_relativos:
                for i in vr:
                    if i != vr[len(vr) - 1]: 
                        i.append(vr[len(vr) - 1])
                vr.pop(len(vr) - 1)
            
            valores_iniciales = copy.deepcopy(valores_relativos[0])
            
            for vi in valores_relativos:
                if vi != valores_relativos[0]:
                    for m, n in zip(vi, valores_iniciales):
                        if len(m) != 1 and len(n) != 1:
                            if m[3] < n[3]:
                                index = vi.index(m)
                                valores_iniciales[index] = m
                            if m[3] == n[3]:
                                val_repetidos.append(m)  
                        elif len(m) != 1 and len(n) == 1:
                            ind = vi.index(m)
                            valores_iniciales[ind] = m   

            for x in valores_iniciales:
                if len(x) > 1:
                    lista_sin_ordenar.append(x)
            for y in val_repetidos:
                if len(y) > 1:
                    lista_de_valores_repetidos.append(y)

        lista_ordenada = sorted(lista_sin_ordenar, key=lambda val: val[3])

        lista_valores_repetidos_ordenados = sorted(lista_ordenada, key=lambda val : val[3])
        return Response({'listaparatoptenproximossaturar':lista_ordenada,'listavaloresrepetidos':lista_valores_repetidos_ordenados},status=status.HTTP_200_OK)
