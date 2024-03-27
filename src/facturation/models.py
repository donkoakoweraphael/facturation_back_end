from django.contrib.auth.models import User
from django.db import models


# Create your models here.


class Client(models.Model):
    telephone = models.CharField(max_length=10)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="client_correspondant", null=True)

    def __str__(self):
        return self.user.username


class Article(models.Model):
    designation = models.CharField(max_length=20)
    prix_unitaire = models.PositiveBigIntegerField()

    def __str__(self):
        return self.designation


class Facture(models.Model):
    numero = models.CharField(max_length=8, blank=True)
    date_de_facturation = models.DateField(auto_now_add=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True)
    total = models.PositiveBigIntegerField(blank=True, null=True)
    totalHT = models.PositiveBigIntegerField(blank=True, null=True)
    tva = models.PositiveBigIntegerField(blank=True, null=True)
    totalTTC = models.PositiveBigIntegerField(blank=True, null=True)
    fichier_de_la_facture = models.FileField(upload_to="factures/", null=True, blank=True)
    message_whatsapp = models.TextField(null=True, blank=True)

    def save(self, **kwargs):
        super().save()
        self.numero = f"FA{self.id:06}"
        super().save()

    def __str__(self):
        return f"{self.numero}"


    def calculer_prix_total(self):
        self.total = sum([l.prixHT for l in self.ligne_de_facturation.all()])

    def calculer_total_hors_taxe(self):
        self.totalHT = self.total

    def calculer_tva(self):
        self.tva = self.totalHT * 0.18

    def calculer_total_toute_taxe_comprise(self):
        self.totalTTC = self.totalHT + self.tva

    def calculer_les_totaux(self):
        self.calculer_prix_total()
        self.calculer_total_hors_taxe()
        self.calculer_tva()
        self.calculer_total_toute_taxe_comprise()
        self.creer_la_facture_pdf()
        self.creer_le_message_whatsapp()
        self.save()

    def liste_des_articles_commandes(self):
        return [[l.article.designation] for l in self.ligne_de_facturation.all()]

    def details_des_articles_commandes(self):
        return [[f"{l.quantite}", f"{l.article.prix_unitaire}", f"{l.prixHT}"] for l in self.ligne_de_facturation.all()]

    def creer_la_facture_pdf(self):
        from django.core.files import File
        import io
        from reportlab.pdfgen.canvas import Canvas

        def creer_le_contenue_du_fichier(c: Canvas):
            def dessiner_un_tableau(tableau, origine_abcisse, origine_ordonne, ecart_ligne, ecart_colonne):
                position_abcisse = origine_abcisse
                position_ordonne = origine_ordonne
                for ligne in tableau:
                    position_abcisse = origine_abcisse
                    for cellule in ligne:
                        c.drawString(position_abcisse, position_ordonne, cellule)
                        position_abcisse += ecart_colonne
                    position_ordonne -= ecart_ligne

            c.drawString(50, 780, "Entreprise :  DAR SARL")
            c.drawString(380, 765, "Client :")
            c.drawString(400, 750, self.client.user.username)
            c.drawString(100, 730, f"N° {self.numero}")
            c.drawString(300, 730, f"{self.date_de_facturation}")

            dessiner_un_tableau(
                [["Designation"]],
                50,
                700,
                20,
                100
            )
            dessiner_un_tableau(
                [["Qté", "Prix unit", "Prix HT"]],
                250,
                700,
                20,
                100
            )
            liste_des_articles_commandes = self.liste_des_articles_commandes()
            dessiner_un_tableau(
                liste_des_articles_commandes,
                50,
                680,
                20,
                100
            )
            details_des_articles_commandes = self.details_des_articles_commandes()
            dessiner_un_tableau(
                details_des_articles_commandes,
                250,
                680,
                20,
                100
            )
            tableau_du_total_simple = [
                ["Total", f"{self.total}"],
            ]
            dessiner_un_tableau(
                tableau_du_total_simple,
                350,
                130,
                20,
                100
            )
            tableau_du_total_ht_et_tva = [
                ["Total HT", f"{self.totalHT}"],
                ["TVA 18 %", f"{self.tva}"],
            ]
            dessiner_un_tableau(
                tableau_du_total_ht_et_tva,
                350,
                100,
                20,
                100
            )
            tableau_du_total_ttc = [
                ["Total TTC", f"{self.totalTTC} FCFA"]
            ]
            dessiner_un_tableau(
                tableau_du_total_ttc,
                350,
                50,
                20,
                100
            )

        buffer = io.BytesIO()
        c = Canvas(buffer)
        creer_le_contenue_du_fichier(c)
        c.showPage()
        c.save()
        self.fichier_de_la_facture = File(file=buffer, name=f"{self.numero}-({self.date_de_facturation}).pdf")

    def creer_le_message_whatsapp(self):
        message = ""
        message += f"""
        Entreprise : DAR SARL
        Client : {self.client.user.username}
        N° {self.numero}
        Date : {self.date_de_facturation}
        """
        for l in self.ligne_de_facturation.all():
            message += f"""
            ----------
            Designation : {l.article.designation}
            Prix unitaire : {l.article.prix_unitaire}
            Quantité : {l.quantite}
            prix HT : {l.prixHT}
            """
        else:
            message += f"""
            ----------
            """
        message += f"""
        Total : {self.total}
        Total HT : {self.totalHT}
        TVA 18 % : {self.tva}
        Total TTC {self.totalTTC} FCFA
        """
        self.message_whatsapp = message


class LigneDeFacturation(models.Model):
    quantite = models.PositiveSmallIntegerField()
    article = models.ForeignKey(Article, on_delete=models.SET_NULL, null=True)
    prixHT = models.PositiveBigIntegerField(blank=True, null=True)
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE, related_name="ligne_de_facturation")

    def __str__(self):
        return f"{self.facture} - {self.article} - x{self.quantite}"

    def save(self, **kwargs):
        super().save()
        self.calculer_prix_hors_taxe()
        super().save()

    def calculer_prix_hors_taxe(self):
        self.prixHT = self.quantite * self.article.prix_unitaire
