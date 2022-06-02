# from msilib import change_sequence
from os import name
from django.http import HttpResponse, JsonResponse
from .models import Test, JsonStore, SnapshotJSON, Doughnuts, Pyramid, Links, Geo, Dropdown, Jitter, AreaType
from .serializers import Tserializers, JsonSerializer, SnapSerializer, DoughnutsSerializer, PyramidSerializer, LinksSerializer, GeoSerializer, DropdownSerializer, JitterSerializer, AreaSerializer
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.cache import cache

import json
from .jitter import JITTER_JSON_DUN
from .geo import MYS_GEOJSON
from .snapshot import DOUGHNUT_JSON, PYRAMID_JSON
from .areas import STATIC_LINKS_JSON, DROPDOWN_JSON, AREAS_JSON
from .jitter import JITTER_JSON_STATE, JITTER_JSON_DISTRICT, JITTER_JSON_PARLIMEN, JITTER_JSON_DUN

class TestJSON(APIView) :
    def get(self, request, format=None):
        # test_list = Test.objects.all()
        # serializer = Tserializers(test_list, many = True)
        test = MYS_GEOJSON
        # f = open("reqbin-verify.txt", "r")
        # data = f.read()
        # return HttpResponse(data)
        return JsonResponse(test, safe=False)        

class Snapshot(APIView) :
    def get(self, request, format=None):
        chosen_param = request.query_params.get('area', None)

        if chosen_param == None:
            return JsonResponse([], safe=False)
        
        doughnut_data = ''
        pyramid_data = ''

        # doughnut_data = cache.get('doughnut_cache')
        doughnut_data = json.loads(DOUGHNUT_JSON)
        if not doughnut_data :
            doughnut_data = Doughnuts.objects.all()
            d_ser = DoughnutsSerializer(doughnut_data, many=True)
            doughnut_data = d_ser.data[0]['general']
            cache.set('doughnut_cache', doughnut_data, None)

        # pyramid_data = cache.get('pyramid_cache')
        pyramid_data = json.loads(PYRAMID_JSON)
        if not pyramid_data :
            pyramid_data = Pyramid.objects.all()
            p_ser = PyramidSerializer(pyramid_data, many=True)
            pyramid_data = p_ser.data[0]['general']
            cache.set('pyramid_cache', pyramid_data, None)

        r_data = {}
        if chosen_param in doughnut_data : 
            r_data['doughnut_charts'] = doughnut_data[chosen_param]
        if chosen_param in pyramid_data :
            r_data['pyramid_charts'] = pyramid_data[chosen_param]
        return JsonResponse(r_data, safe=False)

class DoughnutsJSON(APIView) :
    def get(self, request, format=None):            
        s_param = request.query_params.get('state', None)
        p_param = request.query_params.get('parlimen', None)
        dun_param = request.query_params.get('dun', None)
        dist_param = request.query_params.get('district', None)

        chosen_param = return_by_precedence([dun_param, p_param, dist_param, s_param])

        data = ''

        # doughnut_cache = cache.get('doughnut_cache')
        doughnut_cache = json.loads(DOUGHNUT_JSON)
        if not doughnut_cache :
            json_list = Doughnuts.objects.all()
            serializer = DoughnutsSerializer(json_list, many = True)
            data = serializer.data[0]['general']
            cache.set('doughnut_cache', data, None)
        else : 
            data = doughnut_cache

        if len(data) == 0 or chosen_param == None:
            return JsonResponse([], safe=False)
        
        if chosen_param not in data :
            return JsonResponse([], safe=False)
        else :
            return JsonResponse(data[chosen_param], safe=False)   

class PyramidJSON(APIView) :
    def get(self, request, format=None):
        s_param = request.query_params.get('state', None)
        dist_param = request.query_params.get('district', None)
        chosen_param = return_by_precedence([dist_param, s_param])

        data = ''
        
        # pyramid_cache = cache.get('pyramid_cache')
        pyramid_cache = json.loads(PYRAMID_JSON)
        if not pyramid_cache : 
            json_list = Pyramid.objects.all()
            serializer = PyramidSerializer(json_list, many = True)
            data = serializer.data[0]['general']
            cache.set('pyramid_cache', data, None)
        else : 
            data = pyramid_cache

        if len(data) == 0 or chosen_param == None:
            return JsonResponse([], safe=False)
    
        if chosen_param not in data :
            return JsonResponse([], safe=False)
        else :
            return JsonResponse(data[chosen_param], safe=False)       

class StaticJSON(APIView) :
    def get(self, request, format=None):    
        data = ''

        # static_cache = cache.get('static_cache')
        static_cache = json.loads(STATIC_LINKS_JSON)
        if not static_cache :
            json_list = Links.objects.all()
            serializer = LinksSerializer(json_list, many = True)            
            data = serializer.data[0]['general']
            cache.set('static_cache', data, None)
        else :
            data = static_cache

        if len(data) == 0 :
            return JsonResponse([], safe=False)

        area_type = request.query_params.get('type', None)

        if area_type not in ['state', 'district', 'parlimen', 'dun'] or area_type == None:
            return JsonResponse(data, safe=False)
        else :
            area_type = text_change(area_type)
            return JsonResponse(data[area_type], safe=False)

class GeoJSON(APIView) :
    def get(self, request, format=None):    
        area = request.query_params.get('area', None)
        a_area = ''
        q_id = 0
        q_list = {"state" : 2, "district" : 3, "parlimen" : 4, "dun" : 5}
        
        if area == 'mys' :
            q_id = 1    
            a_area = 'country'
        else :
            a_area = is_valid(area)
            q_id = q_list[a_area]

        if a_area != '' :
            data = ''
            geo_cache = cache.get('geo_' + a_area)

            if not geo_cache :
                json_list = Geo.objects.filter(id=q_id)
                serializer = GeoSerializer(json_list, many = True)
                data = serializer.data[0]['country']
                cache.set("geo_" + a_area, data, None)
            else :
                data = geo_cache

            if a_area != 'country' :
                data = data[area]

            if len(data) == 0 :
                return JsonResponse([], safe=False)
            
            return JsonResponse(data, safe=False)
        else :
            return JsonResponse([], safe=False)

class DropdownJSON(APIView) :
    def get(self, request, format=None):  
        state = request.query_params.get('state', None)
        filter = request.query_params.get('filter', None)
        data = ''

        # dropdown_cache = cache.get('dropdown_cache')
        dropdown_cache = json.loads(DROPDOWN_JSON)
        if not dropdown_cache : 
            json_list = Dropdown.objects.all()
            serializer = DropdownSerializer(json_list, many = True)
            data = serializer.data[0]['dropdown']
            cache.set('dropdown_cache', data, None)
        else :
            data = dropdown_cache

        if len(data) == 0 :
            return JsonResponse([], safe=False)

        if state == None and filter in ['parlimen', 'district', 'dun'] :
            r_data = []
            for x in data :
                if filter in data[x]: 
                    r_data += data[x][filter]
            r_data = sorted(r_data, key=lambda d: d['label'])   
            return JsonResponse(r_data, safe=False)

        if filter in data[state] and in_state(state) : 
            filter = text_change(filter)
            return JsonResponse(data[state][filter], safe=False)
        else :
            return JsonResponse([], safe=False)

class JitterJSON(APIView) :
    def get(self, request, format=None):  
        area = request.query_params.get('area', None)
        r_area = is_valid(area)
        # q_list = {"state" : 1, "district" : 2, "parlimen" : 3, "dun" : 4}
        q_list = {"state" : JITTER_JSON_STATE, "district" : JITTER_JSON_DISTRICT, "parlimen" : JITTER_JSON_PARLIMEN, "dun" : JITTER_JSON_DUN}

        if r_area != '' :
            data = ''
            q_id = q_list[r_area]
            # jitter_cache = cache.get("jitter_" + r_area)
            jitter_cache = json.loads(q_id)
            if not jitter_cache :
                json_list = Jitter.objects.filter(id=q_id)
                serializer = JitterSerializer(json_list, many = True)
                data = serializer.data[0]['jitter']
                cache.set("jitter_" + r_area, data, None)
            else :
                data = jitter_cache

            if len(data) == 0 :
                return JsonResponse([], safe=False)

            return JsonResponse(data, safe=False) 
        else :
            return JsonResponse([], safe=False)        

class AreaJSON(APIView) :
    def get(self, request, format=None):  
        area = request.query_params.get('area', None)
        
        data = ''
        # area_cache = cache.get('area_cache')
        area_cache = json.loads(AREAS_JSON)
        if not area_cache : 
            json_list = AreaType.objects.all()
            serializer = AreaSerializer(json_list, many = True)
            data = serializer.data[0]['area']
            cache.set('area_cache', data, None)
        else :
            data = area_cache

        if len(data) == 0 or area == None :
            return JsonResponse([], safe=False)    

        if area in data :
            return JsonResponse({"area_type" : data[area], 'area_name' : original_name(area) }, safe=False)
        else :
            return JsonResponse([], safe=False)

def original_name(area) :
    STATE_ABBR = {'jhr' : 'Johor',
                    'kdh' : 'Kedah',
                    'ktn' : 'Kelantan', 
                    'kvy' : 'Klang Valley',
                    'mlk' : 'Melaka',
                    'nsn' : 'Negeri Sembilan',
                    'phg' : 'Pahang',
                    'prk' : 'Perak',
                    'pls' : 'Perlis',
                    'png' : 'Pulau Pinang',
                    'sbh' : 'Sabah',
                    'swk' : 'Sarawak',
                    'sgr' : 'Selangor',
                    'trg' : 'Terengganu',
                    'lbn' : 'W.P. Labuan',
                    'pjy' : 'W.P. Putrajaya',
                    'kul' : 'W.P. Kuala Lumpur',
                    'mys' :'Malaysia'}

    if area in STATE_ABBR :
        return STATE_ABBR[area]
    else :
        HARD_CODED_AREAS = {
            'p.018-kulim-bandar-baharu' : 'P.018 Kulim-Bandar Baharu', 
            'n.27-layang-layang': 'N.27 Layang-Layang', 
            'n.20-api-api' : 'N.20 Api-Api', 
            'n.50-gum-gum' : 'N.50 Gum-Gum'}
        if area in HARD_CODED_AREAS :
            return HARD_CODED_AREAS[area]
        else :
            return area.replace("-", " ").title()

def text_change(x) :
    return 'parlimen' if x == 'parliamen' else x

def is_valid(area) :
    data = ''
    
    # area_cache = cache.get('area_cache')
    area_cache = json.loads(AREAS_JSON)
    if not area_cache :
        json_list = AreaType.objects.all()
        serializer = AreaSerializer(json_list, many = True)
        data = serializer.data[0]['area']
        cache.set('area_cache', data, None)
    else :
        data = area_cache
    
    if area in data :
        return data[area]
    else :
        return ''

def in_state(state) :
    state_list = ['jhr', 'kdh', 'ktn', 'kvy', 'mlk', 'nsn', 'phg', 'prk', 'pls', 'png', 'sbh', 'swk', 'sgr', 'trg', 'lbn', 'pjy', 'kul']
    return state in state_list

def return_by_precedence(param_list) :
    for x in param_list :
        if x != None : 
            return x

def insert_json() :
    test = {}
    test['name'] = 'TEST'
    test['age'] = 24
    # json_val = json.dumps(test)
    JsonStore.objects.create(general = test)