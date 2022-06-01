from rest_framework import serializers
from .models import Test, JsonStore, SnapshotJSON, Doughnuts, Pyramid, Links, Geo, Dropdown, Jitter, AreaType

class Tserializers(serializers.ModelSerializer) :
    class Meta : 
        model = Test
        fields = ['id', 'name', 'json']

class JsonSerializer(serializers.ModelSerializer) :
    class Meta : 
        model = JsonStore
        fields = ['general']

class SnapSerializer(serializers.ModelSerializer) :
    class Meta : 
        model = SnapshotJSON
        fields = ['general']        

class DoughnutsSerializer(serializers.ModelSerializer) :
    class Meta : 
        model = Doughnuts
        fields = ['general']

class PyramidSerializer(serializers.ModelSerializer) :
    class Meta : 
        model = Pyramid
        fields = ['general']      

class LinksSerializer(serializers.ModelSerializer) :
    class Meta : 
        model = Links
        fields = ['general']

class GeoSerializer(serializers.ModelSerializer) :
    class Meta : 
        model = Geo
        fields = ['country', 'state', 'district', 'parlimen', 'dun']

class DropdownSerializer(serializers.ModelSerializer) :
    class Meta : 
        model = Dropdown
        fields = ['dropdown'] 

class JitterSerializer(serializers.ModelSerializer) :
    class Meta : 
        model = Jitter
        fields = ['jitter'] 

class AreaSerializer(serializers.ModelSerializer) :
    class Meta : 
        model = AreaType
        fields = ['area']         


