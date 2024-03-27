from rest_framework import serializers
from drf_writable_nested.serializers import WritableNestedModelSerializer
from .models import *
from django.contrib.auth.models import User


class SignUpSerializer(serializers.Serializer):
    nom = serializers.CharField(max_length=50)
    mot_de_passe = serializers.CharField(max_length=30)
    adresse_email = serializers.EmailField()
    telephone = serializers.CharField(max_length=20)

    def create(self, validated_data):
        print(validated_data)
        exiting_user = User.objects.filter(username=validated_data['nom'])
        if not exiting_user:
            user = User.objects.create_user(
                username=validated_data['nom'],
                password=validated_data['mot_de_passe'],
                email=validated_data['adresse_email']
            )
            print(user)
            client = Client.objects.create(
                user=user,
                telephone=validated_data['telephone']
            )
            print(client)
            return validated_data
        return {'nom': "", 'mot_de_passe': "", 'adresse_email': "", 'telephone': ""}
    

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email"]


class ClientSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Client
        fields = ["id", "user", "telephone"]


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ["id", "url", "designation", "prix_unitaire"]


class LigneDeFacturationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LigneDeFacturation
        fields = ["id", "article", "quantite"]


class FactureCreateSerializer(WritableNestedModelSerializer):
    ligne_de_facturation = LigneDeFacturationCreateSerializer(many=True)

    class Meta:
        model = Facture
        fields = ["id", "url", "numero", "date_de_facturation", "ligne_de_facturation"]


class LigneDeFacturationSerializer(serializers.ModelSerializer):
    article = ArticleSerializer()

    class Meta:
        model = LigneDeFacturation
        fields = ["id", "article", "quantite", "prixHT"]


class FactureDetailSerializer(serializers.ModelSerializer):
    client = ClientSerializer()
    ligne_de_facturation = LigneDeFacturationSerializer(many=True)

    class Meta:
        model = Facture
        fields = [
            "id", "url", "numero", "client",
            "date_de_facturation", "ligne_de_facturation",
            "total", "totalHT", "tva", "totalTTC"
        ]


class FactureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Facture
        fields = ["url", "numero", "client", "date_de_facturation"]
