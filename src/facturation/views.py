from django.shortcuts import render
from rest_framework import permissions, viewsets, status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import *
from django.core.mail import EmailMessage
from email.utils import formataddr
from .paramettre import paramettre_email, fonction_de_path
from datetime import datetime, timedelta


# Create your views here.
class SignUpAPIView(generics.CreateAPIView):
    serializer_class = SignUpSerializer


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ClientSerializer


class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated]


class FactureViewSet(viewsets.ModelViewSet):
    serializer_class = FactureSerializer
    create_serializer_class = FactureCreateSerializer
    detail_serializer_class = FactureDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Facture.objects.all()

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update':
            return self.create_serializer_class
        elif self.action == 'retrieve':
            return self.detail_serializer_class
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        res = super().create(request)
        facture = Facture.objects.get(pk=res.data["id"])
        facture.client = request.user.client_correspondant
        facture.calculer_les_totaux()
        envoyer_la_facture_par_email(facture)
        envoyer_la_facture_par_whatsapp(facture)
        return res


def envoyer_la_facture_par_email(facture: Facture):
    message = f"""
    M./Mme {facture.client.user.username}, vous venez de soumettre un formulaire d'achat. Voici votre facture
    """
    subject = "Facturation d'achat"
    from_email = formataddr(("DAR SARL", f"{paramettre_email.EMAIL_SENDER}"))
    print(from_email)
    email_message = EmailMessage(
        subject,
        message,
        from_email,
        [facture.client.user.email]
    )
    email_message.attach(
        facture.fichier_de_la_facture.name.replace('factures/', ''),
        facture.fichier_de_la_facture.read(),
        "application/pdf"
    )
    return email_message.send()


def envoyer_la_facture_par_whatsapp(facture: Facture):
    import pywhatkit
    date_heure_actuelle = datetime.now()
    date_heure_envoi = date_heure_actuelle + timedelta(seconds=120)

    # pywhatkit.sendwhatmsg(
    #     f"+228{facture.client.telephone}",
    #     f"{facture.message_whatsapp}",
    #     date_heure_envoi.hour,
    #     date_heure_envoi.minute,
    #     wait_time=20,
    #     tab_close=True,
    #     close_time=60
    # )

    pywhatkit.sendwhatmsg_instantly(
        f"+228{facture.client.telephone}",
        f"{facture.message_whatsapp}",
        wait_time=20,
        tab_close=True,
        close_time=60
    )

    # pywhatkit.sendwhatmsg_instantly(
    #     f"+228{facture.client.telephone}",
    #     facture.fichier_de_la_facture.read(),
    #     wait_time=20,
    #     tab_close=True,
    #     close_time=60
    # )

    # pywhatkit.sendwhats_image(
    #     f"+228{facture.client.telephone}",
    #     facture.fichier_de_la_facture.read()
    # )
