# MOVENOW 

**Application de digitalisation des motos et taxis au Cameroun**

[![Django](https://img.shields.io/badge/Django-4.2-green)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14-blue)](https://www.postgresql.org/)
[![MORELDEV237](https://img.shields.io/badge/MORELDEV237-blue)](https://www.Moreldev237.org/)

**1️⃣ Présentation Générale*
**1. Contexte**

MOVENOW est une plateforme numérique de mobilité urbaine au Cameroun permettant :

-La réservation de taxis

-La réservation de motos

-La location de véhicules à court ou long terme

-Le covoiturage

-Le paiement via Orange monnaie,MTN monnaie,Carte BANCAIRE et c'est converti en monnaie virtuelle appeller MOVECoin

**-Objectif* : digitaliser le transport urbain camerounais en offrant une solution moderne, sécurisée et optimisée pour les usagers et chauffeurs.

**2️⃣ Objectifs du Projet*
 **Objectifs principaux**

-Digitaliser les transports urbains (motos, taxis, vans, etc.)

-Créer un écosystème économique basé sur le MOVECoin

-Optimiser la gestion des chauffeurs

-Réduire les coûts pour les utilisateurs via des stratégies marketing intelligentes

-Maximiser la rentabilité de MOVENOW

**3️⃣ Architecture Technique*
**3.1 Architecture logicielle**

Backend : Django

Architecture : Multitenancy

Base de données : PostgreSQL

API REST (Django REST Framework)

Authentification :

Email + mot de passe

Google OAuth

Facebook OAuth

**3.2 Multitenancy**

Chaque entité aura son espace isolé :

Tenant Utilisateurs

Tenant Chauffeurs

Tenant Admin

Tenant Entreprises partenaires (évolution future)

**4️⃣ Types d’Utilisateurs*
**👤 4.1 Utilisateur (Client)**

Inscription / Connexion /Deconnexion / Mot de passe oublier

-Réservation véhicule

-Paiement

-Consultation solde MOVECoin

-Historique des trajets

-Covoiturage

**🚖 4.2 Chauffeur*

Inscription avec validation documents

Acceptation / refus de course

Visualisation revenus

Conversion MOVECoin

Dashboard personnalisé

**🛠 4.3 Administrateur*

Validation chauffeurs

Gestion des utilisateurs

Gestion des commissions

Gestion du MOVECoin

Statistiques globales

Paramétrage promotions

**5️⃣ Véhicules Disponibles*

**Types de véhicules :**

🚕 Taxi

🏍 Moto

🛵 Scooter
🚐 Van

👑 VIP

⚰ Corbillard

🛺 Tricycle

🚘 Pickup

**6️⃣ Fonctionnalités Principales*
**6.1 Authentification**

Connexion obligatoire avant la reservation

Social Login (Google / Facebook)

Sessions & Cookies sécurisés

JWT Token pour API

**6.2 Réservation**

Choix du véhicule

Géolocalisation

Estimation prix

Option bagages (-10%)

Option covoiturage (-25%)

Choix chauffeur spécifique

Réservation immédiate ou planifiée

**6.3 Paiement**

Paiement mobile money

Carte bancaire

Portefeuille interne MOVECoin

Après paiement :

Conversion automatique en MOVECoin

Déduction progressive selon les trajets

**7️⃣ Système MOVECoin*
**Principe**

Chaque paiement génère du MOVECoin

Le MOVECoin sert à payer les trajets

Le chauffeur reçoit sa part après commission plateforme

💰 Avantages marketing :

Fidélisation clients

Gamification

Bonus de parrainage

Cashback intelligent

**8️⃣ Stratégie Marketing Rentable*
 **1. Covoiturage (-25%)**

Optimise le remplissage

Réduit les trajets à vide

Augmente volume global

Commission cumulée sur plusieurs passagers

**🎒 2. Bagages (-10%)**

Supplément intégré

Gestion intelligente logistique

**🪙 3. MOVECoin**

Monnaie interne = rétention

Incite à reconsommer

Réduction uniquement en MOVECoin

**🤖 4. Chatbot conversationnel**

Fonctionnalités :

Assistance réservation

FAQ automatisée

Support 24/7

Promotion personnalisée

Suggestions trajet
Interaction possible :

Le chatbot peut proposer des réductions temporaires en échange de fidélité

Gestion dynamique du MOVECoin

**9️⃣ Dashboard*
**👤 Dashboard Utilisateur**

Solde MOVECoin

Historique

Réservation rapide

Promotions

Support chatbot

**🚖 Dashboard Chauffeur**

Courses en attente

Revenus

Notation

Statistiques

Conversion MOVECoin → argent réel

**🛠 Dashboard Admin**

Gestion globale

Validation comptes

Paramétrage réductions

Gestion commissions

Monitoring transactions

Analytics

**🔟 Sécurité**

HTTPS obligatoire

JWT + Refresh Token

Gestion des cookies sécurisés

Protection CSRF

Validation KYC chauffeurs

Historique traçable des transactions

**11️⃣ FAQ – MOVENOW*
❓ Comment devenir chauffeur ?

Inscription

Soumission documents

Validation admin

Activation compte

❓ Comment réserver ?

Connexion

Choix véhicule

Choix destination

Paiement

Confirmation

❓ Comment fonctionne le MOVECoin ?

Chaque paiement génère du MOVECoin

Il est utilisé pour les trajets

Non convertible hors plateforme (sauf chauffeurs)

❓ Puis-je choisir mon chauffeur ?

Oui, si disponible.

❓ Puis-je annuler ?

Oui, selon conditions définies.