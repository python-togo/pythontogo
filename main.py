"""
Python Togo FastAPI application.

This module defines a small FastAPI server that serves HTML templates,
static assets, and a few JSON API endpoints for events, news, communities,
and basic forms (join, contact, partnership).

Notes
-----
- Translations are stored in-memory in `TRANSLATIONS` and selected via
    cookie or `Accept-Language`.
- Sample data for events and news is kept in-memory for simplicity.
"""

from datetime import date
import json
import os
from typing import List, Optional

from dotenv import load_dotenv
from email_validator import EmailNotValidError, validate_email
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from supabase import Client, create_client

app = FastAPI(
    summary="Python Togo official website.",
    description="The Python Software Community Togo's official website.",
    docs_url=None,
    redoc_url=None,
    title="Python Togo",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")
load_dotenv()
SUBABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUBABASE_URL, SUPABASE_KEY)

# Simple in-memory sample data
EVENTS = [
    {
        "id": 1,
        "date": "2024-11-30",
        "location": "Lomé",
        "image": "https://ik.imagekit.io/foscyymdh/pythontogo/paydaytogo2024.avif",
        "link": "https://luma.com/runpiv8k",
        "translations": {
            "fr": {
                "title": "PyDay Togo 2024",
                "description": (
                    "Premier grand événement de la communauté Python Togo, "
                    "également connu comme PyCon Africa Extended – Togo 2024. "
                    "Une journée consacrée à Python, au partage de connaissances, "
                    "à l'open source et au développement de la communauté Python au Togo. "
                    "L'événement a réuni plus de 150 participants."
                ),
            },
            "en": {
                "title": "PyDay Togo 2024",
                "description": (
                    "The first major event of the Python Togo community, also known "
                    "as PyCon Africa Extended – Togo 2024. A day dedicated to Python, "
                    "knowledge sharing, open source and growing the Python community "
                    "in Togo. The event brought together more than 150 participants."
                ),
            },
        },
    },
    {
        "id": 2,
        "date": "2025-07-20 to 2025-08-22",
        "location": "Lomé",
        "image": " https://ik.imagekit.io/foscyymdh/pythontogo/30daysofpython2025.jpeg",
        "link": "https://challenge.pytogo.org/",
        "translations": {
            "fr": {
                "title": "30 Days of Python 2025",
                "description": (
                    "Challenge communautaire d'apprentissage de Python organisé "
                    "dans le cadre de la préparation de PyCon Togo 2025. "
                    "Le programme accompagnait les participants dans leur découverte "
                    "et leur pratique quotidienne de Python."
                ),
            },
            "en": {
                "title": "30 Days of Python 2025",
                "description": (
                    "A community Python learning challenge organized as part of "
                    "the preparation for PyCon Togo 2025. The program helped "
                    "participants learn and practice Python on a daily basis."
                ),
            },
        },
    },
    {
        "id": 3,
        "date": "2025-08-23",
        "location": "Lomé",
        "image": "https://ik.imagekit.io/foscyymdh/pythontogo/pycontg2025.png",
        "link": "https://pycon.pytogo.org/2025",
        "translations": {
            "fr": {
                "title": "PyCon Togo 2025",
                "description": (
                    "Première édition de PyCon Togo, la conférence nationale "
                    "de la communauté Python au Togo. L'événement a réuni "
                    "développeurs, étudiants, professionnels et passionnés "
                    "autour de Python, de l'open source, du développement logiciel "
                    "et du partage de connaissances."
                ),
            },
            "en": {
                "title": "PyCon Togo 2025",
                "description": (
                    "The first edition of PyCon Togo, the national conference "
                    "of the Python community in Togo. The event brought together "
                    "developers, students, professionals and enthusiasts around "
                    "Python, open source, software development and knowledge sharing."
                ),
            },
        },
    },
    {
        "id": 4,
        "date": "2026-06-01 to 2026-06-30",
        "location": "En ligne",
        "image": "https://ik.imagekit.io/foscyymdh/pythontogo/Slide%2016_9%20-%205%20(3).png",
        "link": "https://pycon.pytogo.org/2026/road-to-pycon",
        "translations": {
            "fr": {
                "title": "Road to PyCon Togo 2026",
                "description": (
                    "Série de rencontres et de lives en ligne organisée en amont "
                    "de PyCon Togo 2026. Les épisodes abordent notamment Python, "
                    "l'employabilité, l'entrepreneuriat, l'open source et la construction "
                    "de communautés technologiques durables."
                ),
            },
            "en": {
                "title": "Road to PyCon Togo 2026",
                "description": (
                    "A series of online talks and live sessions organized ahead "
                    "of PyCon Togo 2026. Episodes covered Python, employability, "
                    "entrepreneurship, open source and building sustainable technology communities."
                ),
            },
        },
    },
    {
        "id": 5,
        "date": "2026-07-01 to 2026-07-30",
        "location": "En ligne",
        "image": "https://ik.imagekit.io/foscyymdh/pythontogo/30daysofpythpn.jpeg",
        "link": "https://pycon.pytogo.org/2026/30days",
        "translations": {
            "fr": {
                "title": "30 Days of Python 2026",
                "description": (
                    "Challenge communautaire permettant aux participants de découvrir "
                    "et pratiquer Python pendant 30 jours, dans le cadre de la Road to "
                    "PyCon Togo 2026."
                ),
            },
            "en": {
                "title": "30 Days of Python 2026",
                "description": (
                    "A community challenge designed to help participants learn "
                    "and practice Python for 30 days as part of the Road to "
                    "PyCon Togo 2026 initiative."
                ),
            },
        },
    },
    {
        "id": 6,
        "date": "2026-08-28 to 2026-08-30",
        "location": "Lomé",
        "image": "https://ik.imagekit.io/foscyymdh/images/hoodoe%20art%20-%201.png",
        "link": "https://pycon.pytogo.org/2026",
        "translations": {
            "fr": {
                "title": "PyCon Togo 2026",
                "description": (
                    "Deuxième édition de la conférence nationale Python au Togo. "
                    "PyCon Togo réunit développeurs, étudiants, professionnels, "
                    "entrepreneurs et passionnés autour de Python, de l'open source, "
                    "du développement logiciel, de l'intelligence artificielle "
                    "et de l'innovation."
                ),
            },
            "en": {
                "title": "PyCon Togo 2026",
                "description": (
                    "The second edition of Togo's national Python conference. "
                    "PyCon Togo brings together developers, students, professionals, "
                    "entrepreneurs and enthusiasts around Python, open source, "
                    "software development, artificial intelligence and innovation."
                ),
            },
        },
    },
]


NEWS = [
    {
        "id": 1,
        "date": "2025-05-30",
        "image": "https://ik.imagekit.io/foscyymdh/pythontogo/8f1977e0-7bb6-4ce0-9b42-4c5603b8df6c.webp",
        "link": "https://blog.pytogo.org/the-story-of-python-togo-building-a-strong-python-community-in-togo",
        "translations": {
            "fr": {
                "title": "L'histoire de Python Togo : construire une communauté Python forte au Togo",
                "excerpt": (
                    "Découvrez l'histoire de Python Togo, de ses débuts jusqu'à "
                    "la création de PyDay Togo et la préparation de PyCon Togo."
                ),
                "body": (
                    "Cet article raconte l'histoire de Python Togo, depuis les "
                    "premières expériences communautaires jusqu'à la création "
                    "d'une communauté Python structurée au Togo. Il revient sur "
                    "PyCon Africa 2024, la naissance de Python Togo, PyDay Togo 2024 "
                    "et les premières étapes vers PyCon Togo. "
                    "Lire l'article : "
                    "https://blog.pytogo.org/the-story-of-python-togo-building-a-strong-python-community-in-togo"
                ),
            },
            "en": {
                "title": "The Story of Python Togo: Building a Strong Python Community in Togo",
                "excerpt": (
                    "Discover the story of Python Togo, from its early beginnings "
                    "to PyDay Togo and the creation of a stronger Python community."
                ),
                "body": (
                    "This article tells the story of Python Togo, from its early "
                    "community experiences to the creation of a structured Python "
                    "community in Togo. It covers PyCon Africa 2024, the birth of "
                    "Python Togo, PyDay Togo 2024 and the first steps toward PyCon Togo. "
                    "Read the article: "
                    "https://blog.pytogo.org/the-story-of-python-togo-building-a-strong-python-community-in-togo"
                ),
            },
        },
    },
    {
        "id": 2,
        "date": "2026-04-18",
        "image": "https://ik.imagekit.io/foscyymdh/pythontogo/Slide%2016_9%20-%205%20(3).png",
        "link": "https://blog.pytogo.org/from-zero-to-pycon-building-python-togo-against-the-odds",
        "translations": {
            "fr": {
                "title": "De zéro à PyCon : construire Python Togo malgré les obstacles",
                "excerpt": (
                    "L'histoire de la construction de Python Togo et les défis "
                    "rencontrés pour faire émerger une communauté Python nationale."
                ),
                "body": (
                    "En 2024, Python Togo n'existait pas encore en tant que communauté "
                    "structurée. Cet article revient sur le chemin parcouru, les défis "
                    "rencontrés et les efforts qui ont conduit à la création de PyCon Togo. "
                    "Lire l'article : "
                    "https://blog.pytogo.org/from-zero-to-pycon-building-python-togo-against-the-odds"
                ),
            },
            "en": {
                "title": "From Zero to PyCon: Building Python Togo Against the Odds",
                "excerpt": (
                    "The story of building Python Togo and the challenges faced "
                    "while creating a national Python community."
                ),
                "body": (
                    "In 2024, Python Togo did not yet exist as a structured community. "
                    "This article looks back at the journey, the challenges faced and "
                    "the work that eventually led to PyCon Togo. "
                    "Read the article: "
                    "https://blog.pytogo.org/from-zero-to-pycon-building-python-togo-against-the-odds"
                ),
            },
        },
    },
    {
        "id": 3,
        "date": "2026-04-18",
        "image": "https://ik.imagekit.io/foscyymdh/pythontogo/bf9ed902-5a7c-41c9-b9da-7a605444c899.webp",
        "link": "https://blog.pytogo.org/building-pycon-togo-2026-what-were-learning-from-pycon-colombia",
        "translations": {
            "fr": {
                "title": "Construire PyCon Togo 2026 : ce que nous apprenons de PyCon Colombia",
                "excerpt": (
                    "Les enseignements de PyCon Colombia pour construire une "
                    "édition encore plus forte de PyCon Togo."
                ),
                "body": (
                    "Dans le cadre de la préparation de PyCon Togo 2026, nous "
                    "observons les pratiques d'autres communautés Python afin "
                    "d'améliorer notre organisation. Cet article présente les "
                    "enseignements tirés de PyCon Colombia et leur application "
                    "au contexte de Python Togo. "
                    "Lire l'article : "
                    "https://blog.pytogo.org/building-pycon-togo-2026-what-were-learning-from-pycon-colombia"
                ),
            },
            "en": {
                "title": "Building PyCon Togo 2026: What We're Learning from PyCon Colombia",
                "excerpt": (
                    "Lessons from PyCon Colombia that are helping us build "
                    "a stronger PyCon Togo 2026."
                ),
                "body": (
                    "As we prepare for PyCon Togo 2026, we are looking at other "
                    "Python communities to improve our organization. This article "
                    "explores lessons from PyCon Colombia and how they can be "
                    "applied to the Python Togo community. "
                    "Read the article: "
                    "https://blog.pytogo.org/building-pycon-togo-2026-what-were-learning-from-pycon-colombia"
                ),
            },
        },
    },
]


TRANSLATIONS = {
    "fr": {
        "site-title": "Python Togo",
        "nav-home": "Accueil",
        "nav-about": "À propos",
        "nav-programs": "Programmes",
        "programs-page-title": "Programmes éducatifs",
        "programs-hero-title": "Programmes éducatifs de Python Togo",
        "programs-hero-description": (
            "Python Togo propose des parcours d'apprentissage structurés pour aider "
            "les apprenants à développer des compétences pratiques en programmation, "
            "en ingénierie logicielle et en technologies grâce à l'éducation "
            "communautaire, le mentorat, l'apprentissage entre pairs et la formation "
            "par projet."
        ),
        "programs-card-type": "Type :",
        "programs-card-audience": "Public :",
        "programs-card-focus": "Focus d'apprentissage :",
        "programs-card-certification": "Certification :",
        "programs-card-view": "Voir le programme",
        "programs-view-all": "Voir tous les programmes",
        "programs-education-overview": "Vue d'ensemble de l'éducation",
        "education-page-title": "Éducation à Python Togo",
        "education-hero-title": "Éducation à Python Togo",
        "education-hero-description": (
            "Python Togo propose une éducation technique portée par la communauté "
            "à travers des programmes structurés, le mentorat, la formation pratique, "
            "l'apprentissage entre pairs et le travail sur projet. Nos programmes "
            "s'adressent à des apprenants à différents niveaux, depuis les débutants "
            "qui découvrent Python jusqu'aux futurs ingénieurs logiciels qui développent "
            "des compétences concrètes en développement logiciel, cloud, DevOps et "
            "technologies émergentes."
        ),
        "education-our-programs": "Nos programmes éducatifs",
        "education-learn-more": "En savoir plus",
        "education-philosophy": "Philosophie d'apprentissage",
        "education-practical": "Apprentissage pratique",
        "education-community": "Éducation portée par la communauté",
        "education-collaboration": "Collaboration entre pairs",
        "education-mentorship": "Mentorat",
        "education-open-source": "Culture open source",
        "education-projects": "Développement par projet",
        "education-continuous": "Apprentissage continu",
        "education-accessible": "Éducation technique accessible",
        "education-certificates": "Certificats",
        "education-certificates-desc": "Python Togo délivre des certificats de réussite aux participants qui remplissent avec succès les exigences de ses programmes éducatifs.",
        "education-certificates-link": "En savoir plus sur les certificats",
        "certificates-page-title": "Certificats de Python Togo",
        "certificates-hero-title": "Certificats",
        "certificates-hero-description": (
            "Python Togo délivre des certificats de réussite aux participants "
            "qui remplissent avec succès les exigences de ses programmes éducatifs "
            "structurés."
        ),
        "certificates-policy": "Politique des certificats",
        "certificates-policy-text-1": "Les certificats sont remis après l'achèvement réussi du programme. Les exigences peuvent inclure la participation, les travaux, les projets, les retours des mentors, le travail pratique ou d'autres critères spécifiques au programme.",
        "certificates-policy-text-2": "L'éligibilité au certificat dépend du respect des exigences du programme concerné.",
        "certificates-linked": "Programmes associés aux certificats",
        "program-detail-duration": "Durée",
        "program-detail-type": "Type",
        "program-detail-audience": "Public cible",
        "program-detail-focus": "Focus d'apprentissage",
        "program-detail-learning-topics": "Sujets d'apprentissage",
        "program-detail-learning-approach": "Approche d'apprentissage",
        "program-detail-completion": "Fin du programme et certification",
        "program-detail-completion-text": "Les participants qui complètent avec succès les exigences du programme reçoivent un certificat de réussite délivré par Python Togo.",
        "program-detail-model": "Modèle du programme",
        "program-detail-participants": "Participants visés",
        "program-detail-structure": "Structure du programme",
        "program-detail-phase-1": "Phase 1 : Fondations techniques de base",
        "program-detail-phase-2": "Phase 2 : Stage pratique / Ingénierie appliquée",
        "program-detail-phase-3": "Phase 3 : Parcours de spécialisation",
        "program-detail-learning-outcomes": "Résultats d'apprentissage",
        "program-detail-certification": "Certification",
        "program-detail-certification-text": "Les participants qui remplissent les exigences du bootcamp reçoivent un certificat de réussite ou un certificat de formation professionnelle délivré par Python Togo.",
        "program-detail-mentorship-intro": "Appariement mentor–mentoré : les participants sont jumelés ou mis en relation selon leurs intérêts, objectifs, expérience et disponibilité.",
        "program-detail-program-pathways": "Parcours de spécialisation",
        "program-detail-phase-1-duration": "Durée : 3 mois",
        "program-detail-phase-2-duration": "Durée : 3 mois",
        "program-detail-phase-3-desc": "Le programme établit d'abord une solide base commune en Python et en ingénierie logicielle avant de permettre aux participants de choisir une spécialisation alignée avec leurs intérêts et leurs objectifs de carrière.",
        "program-detail-phase-3-availability": "Les parcours disponibles peuvent varier selon la cohorte, les mentors, les projets et la capacité du programme.",
        "program-detail-availability": "Les parcours disponibles peuvent varier selon la cohorte, les mentors, les projets et la capacité du programme.",
        "nav-code": "Code de conduite",
        "nav-events": "Événements",
        "nav-news": "Actualités",
        "nav-gallery": "Galerie",
        "nav-join": "Adhérer",
        "nav-contact": "Contact",
        "nav-partners": "Partenaires",
        "nav-communities": "Communautés",
        "lang-fr": "FR",
        "lang-en": "EN",
        "donate": "Nous soutenir",
        "footer-about-title": "À propos",
        "footer-about-desc": (
            "Python Togo promeut le langage de programmation Python au Togo."
        ),
        "footer-links-title": "Liens",
        "footer-contact-title": "Contact",
        "footer-logo-by": "Logo conçu avec ❤️ par",
        "footer-site-by": "Ce site a été conçu et développé avec ❤️ par",
        "footer-using": "à l'aide de",
        "footer-and-deployed": "et déployé sur",
        "footer-rights": "Tous droits réservés.",
        "footer-logos": "Logos",
        "gallery-title": "Galerie",
        "gallery-intro": (
            "Découvrez les photos de nos événements et rencontres. Cliquez sur le "
            "lien ci-dessous pour accéder à notre album."
        ),
        "gallery-view": "Voir",
        "gallery-external": "Voir notre galerie",
        "gallery-external-coming": "Voir notre galerie (à venir)",
        "gallery-recent": "Vignettes récentes",
        "join-title": "Adhérer",
        "join-intro": (
            "Rejoignez la communauté Python Togo en remplissant le formulaire "
            "ci-dessous."
        ),
        "label-name": "Nom",
        "label-fullname": "Nom complet",
        "label-email": "Email",
        "label-city": "Ville",
        "label-level": "Niveau Python",
        "level-beginner": "Débutant",
        "level-intermediate": "Intermédiaire",
        "level-advanced": "Avancé",
        "btn-send": "Envoyer",
        "contact-title": "Contact",
        "contact-intro": (
            "Pour toute question, envoyez-nous un message via le formulaire."
        ),
        "label-subject": "Sujet",
        "label-message": "Message",
        "agree-privacy": "J'ai lu et j'accepte la politique de confidentialité",
        "agree-coc": "J'ai lu et j'accepte le Code de conduite",
        "consent-alert": (
            "Veuillez accepter la politique de confidentialité et le Code de "
            "conduite avant de continuer."
        ),
        "privacy-link-text": "Politique de confidentialité",
        "news-title": "Actualités",
        "news-read-more": "Voir plus",
        "news-back": "Retour aux actualités",
        "privacy-title": "Politique de confidentialité",
        "privacy-heading": "Politique de confidentialité",
        "privacy-intro": (
            "Chez Python Togo, nous prenons la confidentialité de vos données au "
            "sérieux. Cette page explique quelles données nous collectons, "
            "pourquoi nous les collectons et comment nous les utilisons."
        ),
        "privacy-collect-heading": "Données que nous collectons",
        "privacy-collect-1": (
            "Données de contact : nom, adresse e‑mail, téléphone (si fournies) "
            "lorsque vous remplissez un formulaire."
        ),
        "privacy-collect-2": (
            "Informations de profil : ville, niveau, intérêts (quand vous les "
            "partagez)."
        ),
        "privacy-collect-3": (
            "Données techniques : adresse IP, type de navigateur et timing des "
            "requêtes pour améliorer nos services."
        ),
        "privacy-why-heading": "Pourquoi nous collectons ces données",
        "privacy-why-intro": "Nous utilisons vos données pour :",
        "privacy-why-1": "Répondre à vos demandes (adhésion, partenariat, contact).",
        "privacy-why-2": "Organiser et informer sur les événements.",
        "privacy-why-3": "Améliorer l'expérience et la sécurité du site.",
        "privacy-share-heading": "Partage et conservation",
        "privacy-share-text": (
            "Nous ne vendons ni ne louons vos données personnelles. Les demandes "
            "reçues peuvent être partagées avec les membres organisateurs et "
            "conservées aussi longtemps que nécessaire pour répondre à la "
            "demande ou se conformer aux obligations légales."
        ),
        "privacy-retention-sub": "Durée de conservation",
        "privacy-retention-intro": (
            "Nous conservons vos données aussi longtemps que nécessaire pour "
            "atteindre les objectifs pour lesquels elles ont été collectées. "
            "Par exemple :"
        ),
        "privacy-retention-1": (
            "Demandes d'adhésion : conservées pendant 3 ans après la dernière "
            "interaction, sauf si vous demandez leur suppression."
        ),
        "privacy-retention-2": (
            "Inscriptions à des événements : conservées pendant la durée "
            "nécessaire à l'organisation et archivées pendant 3 ans pour des "
            "raisons administratives."
        ),
        "privacy-retention-3": (
            "Messages de contact : conservés pendant 2 à 3 ans selon la nature "
            "de la demande."
        ),
        "privacy-disclosure-sub": "Partage et divulgation",
        "privacy-disclosure-text": (
            "Nous ne partageons pas vos données personnelles avec des tiers à des "
            "fins commerciales sans votre consentement explicite. Les données "
            "peuvent être partagées avec des prestataires qui traitent les "
            "données pour notre compte (hébergement, envoi d'emails), sous "
            "contrat de confidentialité."
        ),
        "privacy-rights-heading": "Vos droits",
        "privacy-rights-text": (
            "Vous pouvez demander l'accès, la rectification ou la suppression de "
            "vos données en nous contactant à"
        ),
        "privacy-forms-heading": "Formulaires et consentement",
        "privacy-forms-intro": (
            "Tous les formulaires importants (adhésion, partenariat) exigent votre "
            "consentement explicite :"
        ),
        "privacy-forms-privacy": (
            "Vous devez cocher la case indiquant que vous avez lu et accepté "
            "notre politique de confidentialité."
        ),
        "privacy-forms-coc": (
            "Vous devez cocher la case indiquant que vous acceptez le Code de "
            "conduite de la communauté."
        ),
        "privacy-questions": (
            "Si vous avez des questions sur cette politique, contactez-nous à"
        ),
        "coc-title": "Code de conduite",
        "coc-heading": "Code de conduite",
        "coc-intro": (
            "Cette charte s'inspire des meilleures pratiques utilisées par les "
            "communautés Python, notamment celles de la Python Software "
            "Foundation (PSF). Elle vise à garantir un environnement sûr, "
            "accueillant et professionnel pour toutes et tous, quelles que "
            "soient l'expérience, l'identité ou l'origine."
        ),
        "coc-commitment": "Notre engagement",
        "coc-commitment-intro": "Nous nous engageons à :",
        "coc-commitment-1": (
            "Fournir un espace inclusif et respectueux pour les événements, "
            "forums et canaux en ligne liés à Python Togo."
        ),
        "coc-commitment-2": "Valoriser la diversité des parcours et des contributions.",
        "coc-commitment-3": (
            "Répondre rapidement et de manière confidentielle aux signalements "
            "de comportements inappropriés."
        ),
        "coc-expected": "Comportements attendus",
        "coc-expected-1": "Respecter les autres participants et leurs opinions.",
        "coc-expected-2": (
            "Être attentif(ve) au langage employé et utiliser un ton constructif."
        ),
        "coc-expected-3": (
            "Accepter les retours avec humilité et être prêt(e) à s'excuser en "
            "cas d'erreur."
        ),
        "coc-expected-4": (
            "Respecter les règles spécifiques aux lieux ou aux plateformes "
            "(modération, sécurité, accessibilité)."
        ),
        "coc-unacceptable": "Comportements inacceptables",
        "coc-unacceptable-intro": "Ne seront pas tolérés :",
        "coc-unacceptable-1": (
            "Les propos discriminatoires, le harcèlement, les attaques "
            "personnelles ou menaces."
        ),
        "coc-unacceptable-2": (
            "La diffusion d'insultes, propos sexistes, racistes, homophobes, "
            "transphobes ou tout autre contenu haineux."
        ),
        "coc-unacceptable-3": (
            "Le partage non consenti d'informations personnelles ou confidentielles."
        ),
        "coc-unacceptable-4": (
            "Le non-respect des consignes de sécurité et de modération des "
            "organisateurs."
        ),
        "coc-scope": "Périmètre",
        "coc-scope-text": (
            "Ce code s'applique à tous les espaces officiels et événements "
            "organisés par Python Togo, y compris les réunions en présentiel, "
            "ateliers, conférences, listes de diffusion, forums et canaux de "
            "discussion en ligne associés."
        ),
        "coc-report": "Procédure de signalement",
        "coc-report-intro": (
            "Si vous êtes victime ou témoin d'un comportement inacceptable :"
        ),
        "coc-report-1": (
            "Contactez d'abord les organisateurs via la page de contact ou "
            "envoyez un email à"
        ),
        "coc-report-2": (
            "Fournissez autant de détails que possible : date, lieu, personnes "
            "impliquées, témoins et copies de messages si pertinent."
        ),
        "coc-report-3": (
            "Indiquez si vous souhaitez que votre signalement soit traité de "
            "façon confidentielle."
        ),
        "coc-handling": "Gestion des signalements",
        "coc-handling-text": (
            "Les organisateurs examineront les signalements rapidement et "
            "prendront des mesures proportionnées, qui peuvent inclure :"
        ),
        "coc-handling-1": "Un avertissement formel.",
        "coc-handling-2": "La suspension ou exclusion d'un événement ou d'un canal.",
        "coc-handling-3": (
            "La communication d'informations aux autorités compétentes si nécessaire."
        ),
        "coc-confidentiality": "Confidentialité et protection",
        "coc-confidentiality-text": (
            "Les informations reçues dans le cadre d'un signalement seront "
            "traitées avec la plus grande confidentialité possible. Seules les "
            "personnes nécessaires à l'enquête auront accès aux informations."
        ),
        "coc-examples": "Exemples",
        "coc-examples-intro": "Exemples de comportements à signaler :",
        "coc-examples-1": (
            "Messages répétés et non sollicités d'un individu visant une autre "
            "personne."
        ),
        "coc-examples-2": (
            "Commentaires à caractère discriminatoire sur la base d'une identité."
        ),
        "coc-examples-3": "Partage d'une photo privée sans consentement.",
        "coc-organizers": "Responsabilités des organisateurs",
        "coc-organizers-intro": "Les organisateurs s'engagent à :",
        "coc-organizers-1": (
            "Maintenir des procédures claires pour la gestion des incidents."
        ),
        "coc-organizers-2": (
            "Former, si nécessaire, les modérateurs et responsables à la "
            "gestion des signalements."
        ),
        "coc-organizers-3": (
            "Publier des mises à jour sur les mesures prises, sans compromettre "
            "la confidentialité."
        ),
        "coc-revision": "Révision",
        "coc-revision-text": (
            "Ce code de conduite pourra être revu périodiquement pour s'adapter "
            "aux retours de la communauté et aux bonnes pratiques "
            "internationales."
        ),
        "coc-thanks": (
            "Merci de contribuer à faire de Python Togo un espace sûr et "
            "accueillant pour tous."
        ),
        "home-title": "Accueil",
        "home-welcome": "Bienvenue sur Python Togo",
        "home-intro": (
            "Python Togo est une communauté de développeurs et passionnés Python "
            "au Togo. Nous organisons des événements, des formations et "
            "promouvons l'usage de Python dans notre pays."
        ),
        "home-join": "Rejoindre la communauté",
        "home-view-events": "Voir les événements",
        "home-news-recent": "Actualités récentes",
        "home-news-all": "Voir toutes les actualités",
        "partners-our": "Nos partenaires",
        "partners-intro": (
            "Nous remercions les organisations et individus qui nous font confiance."
        ),
        "partners-none": "Aucun partenaire pour le moment.",
        "partners-request-title": "Demander un partenariat",
        "partners-request-intro": (
            "Vous souhaitez nous soutenir ou devenir partenaire ? "
            "Envoyez votre demande ci-dessous."
        ),
        "label-organization": "Organisation",
        "label-contact-name": "Nom du contact",
        "label-website-optional": "Site web (optionnel)",
        "label-message-optional": "Message (optionnel)",
        "partners-send": "Envoyer la demande",
        "partners-sending": "Envoi en cours...",
        "partners-success": "Demande envoyée, merci !",
        "partners-error-prefix": "Erreur: ",
        "partners-network-error-prefix": "Erreur réseau: ",
        "about-title": "À propos",
        "about-heading": "À propos",
        "about-blurb": (
            "Python Togo rassemble les développeurs, étudiants et professionnels "
            "utilisant Python au Togo. Notre mission est de promouvoir "
            "l'apprentissage et l'utilisation de Python."
        ),
        "about-mission": "Notre mission",
        "about-m1": "Promouvoir l'apprentissage et l'utilisation de Python",
        "about-m2": "Organiser des événements et formations",
        "about-m3": "Favoriser le partage de connaissances",
        "events-title": "Événements",
        "events-heading": "Événements",
        "events-sample-meta": "2025-12-05 • Lomé",
        "events-sample-title": "Atelier Python débutant",
        "events-sample-desc": "Introduction à Python pour les nouveaux développeurs.",
        "communities-title": "Communautés",
        "communities-heading": "Communautés locales",
        "communities-card-title": "Python Togo",
        "communities-card-desc": (
            "Groupe local basé à Lomé, rencontre mensuelle et ateliers."
        ),
        "error-404-title": "Page non trouvée",
        "error-404-heading": "Erreur 404",
        "error-404-message": "Désolé, la page que vous recherchez n'existe pas.",
        "error-404-home": "Retour à l'accueil",
        "error-500-title": "Erreur serveur",
        "error-500-heading": "Erreur 500",
        "error-500-message": (
            "Une erreur interne s'est produite. Veuillez réessayer plus tard."
        ),
        "error-403-title": "Accès interdit",
        "error-403-heading": "Erreur 403",
        "error-403-message": "Vous n'avez pas la permission d'accéder à cette page.",
        "error-generic-title": "Erreur",
        "error-generic-heading": "Une erreur s'est produite",
        "error-generic-message": "Quelque chose s'est mal passé. Veuillez réessayer.",
    },
    "en": {
        "site-title": "Python Togo",
        "nav-home": "Home",
        "nav-about": "About",
        "nav-programs": "Programs",
        "programs-page-title": "Educational Programs",
        "programs-hero-title": "Python Togo Educational Programs",
        "programs-hero-description": (
            "Python Togo offers structured learning opportunities designed to help learners build practical programming, software engineering, and technology skills through community-led education, mentorship, peer learning, and project-based training."
        ),
        "programs-card-type": "Type:",
        "programs-card-audience": "Audience:",
        "programs-card-focus": "Learning focus:",
        "programs-card-certification": "Certification:",
        "programs-card-view": "View program",
        "programs-view-all": "View all programs",
        "programs-education-overview": "Education overview",
        "education-page-title": "Education at Python Togo",
        "education-hero-title": "Education at Python Togo",
        "education-hero-description": (
            "Python Togo provides community-driven technical education through structured programs, mentorship, practical training, peer learning, and project-based learning. Our programs support learners at different stages, from beginners discovering Python to aspiring software engineers developing practical skills in software development, cloud infrastructure, DevOps, and emerging technologies."
        ),
        "education-our-programs": "Our Educational Programs",
        "education-learn-more": "Learn more",
        "education-philosophy": "Learning Philosophy",
        "education-practical": "Practical learning",
        "education-community": "Community-driven education",
        "education-collaboration": "Peer collaboration",
        "education-mentorship": "Mentorship",
        "education-open-source": "Open-source culture",
        "education-projects": "Project-based development",
        "education-continuous": "Continuous learning",
        "education-accessible": "Accessible technical education",
        "education-certificates": "Certificates",
        "education-certificates-desc": "Python Togo issues certificates of completion to participants who successfully fulfill the requirements of its educational programs.",
        "education-certificates-link": "Learn about certificates",
        "certificates-page-title": "Python Togo Certificates",
        "certificates-hero-title": "Certificates",
        "certificates-hero-description": (
            "Python Togo provides certificates of completion to participants who successfully fulfill the requirements of its structured educational programs."
        ),
        "certificates-policy": "Certificate policy",
        "certificates-policy-text-1": "Certificates are awarded after successful completion. Requirements may include participation, assignments, projects, mentor feedback, practical work, or other program-specific criteria.",
        "certificates-policy-text-2": "Certificate eligibility depends on fulfilling the requirements of the relevant program.",
        "certificates-linked": "Programs associated with certificates",
        "program-detail-duration": "Duration",
        "program-detail-type": "Type",
        "program-detail-audience": "Target audience",
        "program-detail-focus": "Learning focus",
        "program-detail-learning-topics": "Learning Topics",
        "program-detail-learning-approach": "Learning Approach",
        "program-detail-completion": "Completion and Certification",
        "program-detail-completion-text": "Participants who successfully complete the program requirements receive a Certificate of Completion issued by Python Togo.",
        "program-detail-model": "Program Model",
        "program-detail-participants": "Intended Participants",
        "program-detail-structure": "Program Structure",
        "program-detail-phase-1": "Phase 1: Core Engineering Foundation",
        "program-detail-phase-2": "Phase 2: Practical Internship / Applied Engineering",
        "program-detail-phase-3": "Phase 3: Specialization Pathways",
        "program-detail-learning-outcomes": "Learning Outcomes",
        "program-detail-certification": "Certification",
        "program-detail-certification-text": "Participants who successfully complete the bootcamp requirements receive a Certificate of Completion or Certificate of Professional Training issued by Python Togo.",
        "program-detail-mentorship-intro": "Mentor–mentee pairing: participants are matched or connected according to relevant interests, goals, experience, and availability.",
        "program-detail-availability": "The program first establishes a strong common foundation in Python and software engineering before allowing participants to choose a specialization aligned with their interests and career goals.",
        "program-detail-phase-1-duration": "Duration: 3 months",
        "program-detail-phase-2-duration": "Duration: 3 months",
        "program-detail-phase-3-desc": "The program first establishes a strong common foundation in Python and software engineering before allowing participants to choose a specialization aligned with their interests and career goals.",
        "program-detail-phase-3-availability": "Available pathways may vary by cohort, mentors, projects, and program capacity.",
        "nav-code": "Code of Conduct",
        "nav-events": "Events",
        "nav-news": "News",
        "nav-gallery": "Gallery",
        "nav-join": "Join",
        "nav-contact": "Contact",
        "nav-partners": "Partners",
        "nav-communities": "Communities",
        "lang-fr": "FR",
        "lang-en": "EN",
        "donate": "Support us",
        "footer-about-title": "About",
        "footer-about-desc": (
            "Python Togo promotes the Python programming language in Togo."
        ),
        "footer-links-title": "Links",
        "footer-contact-title": "Contact",
        "footer-logo-by": "Logo designed with ❤️ by",
        "footer-site-by": "This site was designed and developed with ❤️ by",
        "footer-using": "using",
        "footer-and-deployed": "and deployed on",
        "footer-rights": "All rights reserved.",
        "footer-logos": "Logos",
        "gallery-title": "Gallery",
        "gallery-intro": (
            "Discover photos from our events and meetups. Use the link below "
            "to access our album."
        ),
        "gallery-view": "View",
        "gallery-external": "View our gallery",
        "gallery-external-coming": "View our gallery (coming soon)",
        "gallery-recent": "Recent thumbnails",
        "join-title": "Join",
        "join-intro": ("Join the Python Togo community by filling out the form below."),
        "label-name": "Name",
        "label-fullname": "Full name",
        "label-email": "Email",
        "label-city": "City",
        "label-level": "Python level",
        "level-beginner": "Beginner",
        "level-intermediate": "Intermediate",
        "level-advanced": "Advanced",
        "btn-send": "Send",
        "contact-title": "Contact",
        "contact-intro": ("For any questions, send us a message using the form."),
        "label-subject": "Subject",
        "label-message": "Message",
        "agree-privacy": "I have read and agree to the privacy policy",
        "agree-coc": "I have read and agree to the Code of Conduct",
        "consent-alert": (
            "Please accept the privacy policy and Code of Conduct before continuing."
        ),
        "privacy-link-text": "Privacy Policy",
        "news-title": "News",
        "news-read-more": "Read more",
        "news-back": "Back to news",
        "privacy-title": "Privacy Policy",
        "privacy-heading": "Privacy Policy",
        "privacy-intro": (
            "At Python Togo, we take your data privacy seriously. This page "
            "explains what data we collect, why we collect it, and how we use "
            "it."
        ),
        "privacy-collect-heading": "Data we collect",
        "privacy-collect-1": (
            "Contact data: name, email address, phone (if provided) when you "
            "fill out a form."
        ),
        "privacy-collect-2": (
            "Profile information: city, level, interests (when you share them)."
        ),
        "privacy-collect-3": (
            "Technical data: IP address, browser type, and request timing to "
            "improve our services."
        ),
        "privacy-why-heading": "Why we collect this data",
        "privacy-why-intro": "We use your data to:",
        "privacy-why-1": "Respond to your requests (membership, partnership, contact).",
        "privacy-why-2": "Organize and inform about events.",
        "privacy-why-3": "Improve the site experience and security.",
        "privacy-share-heading": "Sharing and retention",
        "privacy-share-text": (
            "We do not sell or rent your personal data. Requests we receive "
            "may be shared with organizing members and kept as long as "
            "necessary to respond or comply with legal obligations."
        ),
        "privacy-retention-sub": "Retention period",
        "privacy-retention-intro": (
            "We retain your data as long as necessary to achieve the purposes "
            "for which it was collected. For example:"
        ),
        "privacy-retention-1": (
            "Membership requests: kept for 3 years after the last interaction, "
            "unless you request deletion."
        ),
        "privacy-retention-2": (
            "Event registrations: kept for the time needed to organize and "
            "archived for 3 years for administrative reasons."
        ),
        "privacy-retention-3": (
            "Contact messages: kept for 2–3 years depending on the nature of "
            "the request."
        ),
        "privacy-disclosure-sub": "Sharing and disclosure",
        "privacy-disclosure-text": (
            "We do not share your personal data with third parties for "
            "commercial purposes without your explicit consent. Data may be "
            "shared with providers processing data on our behalf (hosting, "
            "email delivery) under confidentiality agreements."
        ),
        "privacy-rights-heading": "Your rights",
        "privacy-rights-text": (
            "You can request access, rectification, or deletion of your data "
            "by emailing"
        ),
        "privacy-forms-heading": "Forms and consent",
        "privacy-forms-intro": (
            "All key forms (membership, partnership) require your explicit consent:"
        ),
        "privacy-forms-privacy": (
            "You must check the box indicating you have read and accepted our "
            "privacy policy."
        ),
        "privacy-forms-coc": (
            "You must check the box indicating you accept the community's Code "
            "of Conduct."
        ),
        "privacy-questions": ("If you have questions about this policy, contact us at"),
        "coc-title": "Code of Conduct",
        "coc-heading": "Code of Conduct",
        "coc-intro": (
            "This charter draws on best practices used by Python communities, "
            "including the Python Software Foundation (PSF). It aims to ensure "
            "a safe, welcoming, and professional environment for everyone, "
            "regardless of experience, identity, or background."
        ),
        "coc-commitment": "Our commitment",
        "coc-commitment-intro": "We commit to:",
        "coc-commitment-1": (
            "Provide an inclusive and respectful space for events, forums, and "
            "online channels related to Python Togo."
        ),
        "coc-commitment-2": "Value diverse backgrounds and contributions.",
        "coc-commitment-3": (
            "Respond quickly and confidentially to reports of inappropriate behavior."
        ),
        "coc-expected": "Expected behavior",
        "coc-expected-1": "Respect other participants and their opinions.",
        "coc-expected-2": ("Be mindful of language and use a constructive tone."),
        "coc-expected-3": (
            "Accept feedback humbly and be willing to apologize when wrong."
        ),
        "coc-expected-4": (
            "Respect venue- or platform-specific rules (moderation, safety, "
            "accessibility)."
        ),
        "coc-unacceptable": "Unacceptable behavior",
        "coc-unacceptable-intro": "The following will not be tolerated:",
        "coc-unacceptable-1": (
            "Discriminatory remarks, harassment, personal attacks, or threats."
        ),
        "coc-unacceptable-2": (
            "Insults; sexist, racist, homophobic, or transphobic remarks; or "
            "any hateful content."
        ),
        "coc-unacceptable-3": (
            "Sharing personal or confidential information without consent."
        ),
        "coc-unacceptable-4": (
            "Failing to follow safety and moderation guidelines from organizers."
        ),
        "coc-scope": "Scope",
        "coc-scope-text": (
            "This code applies to all official spaces and events organized by "
            "Python Togo, including in-person meetings, workshops, "
            "conferences, mailing lists, forums, and associated online "
            "channels."
        ),
        "coc-report": "Reporting procedure",
        "coc-report-intro": (
            "If you are a victim or witness of unacceptable behavior:"
        ),
        "coc-report-1": ("First, contact the organizers via the contact page or email"),
        "coc-report-2": (
            "Provide as many details as possible: date, location, people "
            "involved, witnesses, and message copies if relevant."
        ),
        "coc-report-3": (
            "Indicate if you wish your report to be handled confidentially."
        ),
        "coc-handling": "Handling reports",
        "coc-handling-text": (
            "Organizers will review reports promptly and take proportionate "
            "measures, which may include:"
        ),
        "coc-handling-1": "A formal warning.",
        "coc-handling-2": "Suspension or exclusion from an event or channel.",
        "coc-handling-3": ("Informing authorities if necessary."),
        "coc-confidentiality": "Confidentiality and protection",
        "coc-confidentiality-text": (
            "Information received in connection with a report will be handled "
            "with the greatest possible confidentiality. Only people "
            "necessary for the investigation will have access."
        ),
        "coc-examples": "Examples",
        "coc-examples-intro": "Examples of behaviors to report:",
        "coc-examples-1": (
            "Repeated, unsolicited messages from one individual targeting "
            "another person."
        ),
        "coc-examples-2": "Discriminatory comments based on identity.",
        "coc-examples-3": "Sharing a private photo without consent.",
        "coc-organizers": "Organizers' responsibilities",
        "coc-organizers-intro": "Organizers commit to:",
        "coc-organizers-1": ("Maintain clear procedures for incident handling."),
        "coc-organizers-2": (
            "Train moderators and leads, if needed, on handling reports."
        ),
        "coc-organizers-3": (
            "Publish updates on actions taken without compromising confidentiality."
        ),
        "coc-revision": "Revision",
        "coc-revision-text": (
            "This code of conduct may be reviewed periodically to reflect "
            "community feedback and international best practices."
        ),
        "coc-thanks": (
            "Thank you for helping make Python Togo a safe and welcoming space for all."
        ),
        "home-title": "Home",
        "home-welcome": "Welcome to Python Togo",
        "home-intro": (
            "Python Togo is a community of Python developers and enthusiasts in "
            "Togo. We organize events, trainings, and promote the use of "
            "Python across the country."
        ),
        "home-join": "Join the community",
        "home-view-events": "View events",
        "home-news-recent": "Recent news",
        "home-news-all": "See all news",
        "partners-our": "Our partners",
        "partners-intro": (
            "We thank the organizations and individuals who support us."
        ),
        "partners-none": "No partners yet.",
        "partners-request-title": "Request a partnership",
        "partners-request-intro": (
            "Would you like to support us or become a partner? Send your request below."
        ),
        "label-organization": "Organization",
        "label-contact-name": "Contact name",
        "label-website-optional": "Website (optional)",
        "label-message-optional": "Message (optional)",
        "partners-send": "Send request",
        "partners-sending": "Sending...",
        "partners-success": "Request sent, thank you!",
        "partners-error-prefix": "Error: ",
        "partners-network-error-prefix": "Network error: ",
        "about-title": "About",
        "about-heading": "About",
        "about-blurb": (
            "Python Togo brings together developers, students, and "
            "professionals using Python in Togo. Our mission is to promote "
            "learning and use of Python."
        ),
        "about-mission": "Our mission",
        "about-m1": "Promote learning and use of Python",
        "about-m2": "Organize events and training",
        "about-m3": "Encourage knowledge sharing",
        "events-title": "Events",
        "events-heading": "Events",
        "events-sample-meta": "2025-12-05 • Lomé",
        "events-sample-title": "Beginner Python workshop",
        "events-sample-desc": "Introduction to Python for new developers.",
        "communities-title": "Communities",
        "communities-heading": "Local communities",
        "communities-card-title": "Python Togo",
        "communities-card-desc": (
            "Local group based in Lomé, monthly meetups and workshops."
        ),
        "error-404-title": "Page not found",
        "error-404-heading": "Error 404",
        "error-404-message": "Sorry, the page you are looking for does not exist.",
        "error-404-home": "Back to home",
        "error-500-title": "Server error",
        "error-500-heading": "Error 500",
        "error-500-message": "An internal error occurred. Please try again later.",
        "error-403-title": "Access forbidden",
        "error-403-heading": "Error 403",
        "error-403-message": "You do not have permission to access this page.",
        "error-generic-title": "Error",
        "error-generic-heading": "An error occurred",
        "error-generic-message": "Something went wrong. Please try again.",
    },
}
DONATE_URL = "https://pycon.pytogo.org/donate"


@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Handle 404 errors with a custom bilingual page.

    Parameters
    ----------
    request : fastapi.Request
        The incoming HTTP request.
    exc : fastapi.HTTPException
        The HTTP exception that was raised. Contains status code and detail.
    Returns
    -------
    fastapi.responses.TemplateResponse
        The rendered 404 error page with appropriate context.
    """
    lang = get_language(request)
    return templates.TemplateResponse(
        request=request,
        name="error.html",
        status_code=404,
        context=ctx(
            request,
            {
                "status_code": 404,
                "title_key": "error-404-title",
                "heading_key": "error-404-heading",
                "message_key": "error-404-message",
                "detail": None,
                "meta_title": TRANSLATIONS[lang]["error-404-title"] + " — Python Togo",
                "meta_description": TRANSLATIONS[lang]["error-404-message"],
            },
        ),
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception):
    """Handle 500 errors with a custom bilingual page.

    Parameters
    ----------
    request : fastapi.Request
        The incoming HTTP request.
    exc : Exception
        The exception that was raised.
    Returns
    -------
    fastapi.responses.TemplateResponse
        The rendered 500 error page with appropriate context.
    """
    lang = get_language(request)
    return templates.TemplateResponse(
        request=request,
        name="error.html",
        status_code=500,
        context=ctx(
            request,
            {
                "status_code": 500,
                "title_key": "error-500-title",
                "heading_key": "error-500-heading",
                "message_key": "error-500-message",
                "detail": None,
                "meta_title": TRANSLATIONS[lang]["error-500-title"] + " — Python Togo",
                "meta_description": TRANSLATIONS[lang]["error-500-message"],
            },
        ),
    )


@app.exception_handler(403)
async def forbidden_handler(request: Request, exc: HTTPException):
    """Handle 403 errors with a custom bilingual page.

    Parameters
    ----------
    request : fastapi.Request
        The incoming HTTP request.
    exc : fastapi.HTTPException
        The HTTP exception that was raised. Contains status code and detail.
    Returns
    -------
    fastapi.responses.TemplateResponse
        The rendered 403 error page with appropriate context.
    """
    lang = get_language(request)
    return templates.TemplateResponse(
        request=request,
        name="error.html",
        status_code=403,
        context=ctx(
            request,
            {
                "status_code": 403,
                "title_key": "error-403-title",
                "heading_key": "error-403-heading",
                "message_key": "error-403-message",
                "detail": None,
                "meta_title": TRANSLATIONS[lang]["error-403-title"] + " — Python Togo",
                "meta_description": TRANSLATIONS[lang]["error-403-message"],
            },
        ),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle generic HTTP exceptions with a custom bilingual page.
    Parameters
    ----------
    request : fastapi.Request
        The incoming HTTP request.
    exc : fastapi.HTTPException
        The HTTP exception that was raised. Contains status code and detail.
    Returns
    -------
    fastapi.responses.TemplateResponse
        The rendered error page with appropriate status code and context.
    """
    lang = get_language(request)

    error_map = {
        404: ("error-404-title", "error-404-heading", "error-404-message"),
        403: ("error-403-title", "error-403-heading", "error-403-message"),
        500: ("error-500-title", "error-500-heading", "error-500-message"),
    }

    if exc.status_code in error_map:
        title_key, heading_key, message_key = error_map[exc.status_code]
    else:
        title_key, heading_key, message_key = (
            "error-generic-title",
            "error-generic-heading",
            "error-generic-message",
        )

    return templates.TemplateResponse(
        request=request,
        name="error.html",
        status_code=exc.status_code,
        context=ctx(
            request,
            {
                "status_code": exc.status_code,
                "title_key": title_key,
                "heading_key": heading_key,
                "message_key": message_key,
                "detail": exc.detail if hasattr(exc, "detail") else None,
                "meta_title": TRANSLATIONS[lang][title_key] + " — Python Togo",
                "meta_description": TRANSLATIONS[lang][message_key],
            },
        ),
    )


def get_language(request: Request) -> str:
    """
    Determine the preferred language for the request.

    Parameters
    ----------
    request : fastapi.Request
        The incoming HTTP request.

    Returns
    -------
    str
        The language code ("fr" or "en"). Defaults to "fr" if none matched.
    """
    # 1) Query param takes precedence for SEO-friendly alternate URLs
    query_lang = request.query_params.get(
        "lang") or request.query_params.get("hl")
    if query_lang in TRANSLATIONS:
        return query_lang
    # 2) Cookie value
    cookie_lang = request.cookies.get("lang")
    if cookie_lang in TRANSLATIONS:
        return cookie_lang
    # Fallback to Accept-Language
    accept = request.headers.get("accept-language", "")
    if accept:
        for part in accept.split(","):
            code = part.split(";")[0].strip().lower()
            if code.startswith("fr"):
                return "fr"
            if code.startswith("en"):
                return "en"
    return "fr"


@app.get("/lang/{lang_code}")
async def set_language(lang_code: str, request: Request):
    """
    Set the UI language preference via cookie and redirect back.

    Parameters
    ----------
    lang_code : str
        Language code to set ("fr" or "en").
    request : fastapi.Request
        The incoming request, used to read referer.

    Returns
    -------
    fastapi.responses.RedirectResponse
        Redirects to the referer while setting the `lang` cookie.
    """
    if lang_code not in TRANSLATIONS:
        raise HTTPException(status_code=404, detail="Language not supported")
    referer = request.headers.get("referer") or "/"
    resp = RedirectResponse(url=referer, status_code=307)
    resp.set_cookie(
        "lang", lang_code, max_age=60 * 60 * 24 * 365, httponly=False, samesite="lax"
    )
    return resp


def ctx(request: Request, extra: Optional[dict] = None) -> dict:
    """
    Build the template context dictionary.

    Parameters
    ----------
    request : fastapi.Request
        The incoming request used to derive language and cookies.
    extra : dict, optional
        Additional context values to merge.

    Returns
    -------
    dict
        The context including year, language, translations, and extras.
    """
    lang = get_language(request)
    base = {
        "current_year": current_year,
        "lang": lang,
        "t": TRANSLATIONS.get(lang, {}),
        "donate_url": DONATE_URL,
    }
    if extra:
        base.update(extra)
    return base


current_year = date.today().strftime("%Y")
# Configurable donate URL (set DONATE_URL env var). Defaults to '#'.


class JoinRequest(BaseModel):
    full_name: str
    email: str
    city: Optional[str] = None
    level: Optional[str] = None
    agree_privacy: bool
    agree_coc: bool


class PartnershipRequest(BaseModel):
    organization: str
    contact_name: str
    email: str
    website: Optional[str] = None
    message: Optional[str] = None
    agree_privacy: bool
    agree_coc: bool


class ContactSubmit(BaseModel):
    name: str
    email: str
    subject: str
    message: str
    agree_privacy: bool
    agree_coc: bool


def get_data(table):
    """Fetch all data from a given Supabase table.

    Parameters
    ----------
    table : str
        The name of the table to query.

    Returns
    -------
    list of dict
        The list of records from the table, or empty list on error.
    """
    try:
        response = supabase.table(table).select("*").execute()
        if hasattr(response, "data"):
            return response.data or []
        elif isinstance(response, dict):
            return response.get("data", []) or []
        return []
    except Exception as e:
        print(f"Error fetching data from {table}: {e}")
        return []


def insert_data(table, data):
    """Insert data into a given Supabase table.

    Parameters
    ----------
    table : str
        The name of the table to insert into.
    data : dict
        The data to insert.
    Returns
    -------
    bool
        True if insertion was successful, False otherwise.
    """
    try:
        # Accept dict/list or JSON string; ensure we send a list of records
        payload = data
        if isinstance(data, str):
            try:
                payload = json.loads(data)
            except Exception:
                payload = {"payload": data}
        if isinstance(payload, dict):
            payload = [payload]

        print(f"Inserting into {table}: {payload}")
        resp = supabase.table(table).insert(payload[0]).execute()
        err = None
        if hasattr(resp, "error"):
            err = resp.error
        elif isinstance(resp, dict):
            err = resp.get("error")
        if err:
            print(f"Supabase insert error into {table}: {err}")
            return False
        return True
    except Exception as e:
        print(f"Error inserting data into {table}: {e}")
        return False


PARTNERS = get_data("partners")

GALLERIES = get_data("galleries")

JOIN_REQUESTS: List[dict] = []
CONTACT_MESSAGES: List[dict] = []


# Template routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Render the home page with recent news and partners.

    This view assembles recent news items and partner logos for display
    on the landing page.

    Parameters
    ----------
    request : fastapi.Request
        The incoming request.

    Returns
    -------
    fastapi.responses.HTMLResponse
        Rendered template response.

    See Also
    --------
    actualities : News listing page
    partners : Partners page

    Examples
    --------
    Access via browser: ``GET /``
    """
    lang = get_language(request)
    news_items = []
    for n in NEWS:
        tr = n.get("translations", {}).get(lang, {})
        img = n.get(
            "image") or f"https://picsum.photos/seed/news-{n['id']}/600/340"
        news_items.append(
            {
                "id": n["id"],
                "date": n["date"],
                "title": tr.get("title", ""),
                "excerpt": tr.get("excerpt", ""),
                "image": img,
            }
        )
    # show the most recent 2
    news_items = sorted(news_items, key=lambda x: x["date"], reverse=True)[:2]
    return templates.TemplateResponse(
        name="home.html",
        request=request,
        context=ctx(
            request,
            {
                "partners": PARTNERS,
                "news_home": news_items,
                "meta_title": TRANSLATIONS[lang]["home-title"] + " — Python Togo",
                "meta_description": TRANSLATIONS[lang]["footer-about-desc"],
            },
        ),
    )


@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    """
    Render the about page.

    Parameters
    ----------
    request : fastapi.Request
        The incoming request.

    Returns
    -------
    fastapi.responses.HTMLResponse
        Rendered template response.

    Examples
    --------
    ``GET /about``
    """
    lang = get_language(request)
    return templates.TemplateResponse(
        name="about.html",
        request=request,
        context=ctx(
            request,
            {
                "meta_title": TRANSLATIONS[lang]["about-title"] + " — Python Togo",
                "meta_description": TRANSLATIONS[lang]["about-blurb"],
            },
        ),
    )


PROGRAMS = [
    {
        "slug": "30-days-of-python",
        "name": "30 Days of Python",
        "url": "/programs/30-days-of-python",
        "duration": "30 days",
        "type": "Short-term introductory Python learning program",
        "audience": "Beginners, students, and self-taught learners",
        "focus": "Python fundamentals and programming foundations",
        "certificate": "Certificate of Completion for participants who successfully complete the program requirements.",
        "short_description": "A structured 30-day learning journey designed to introduce participants to Python and build a solid software development foundation.",
        "description": "30 Days of Python is a structured 30-day learning program designed to introduce participants to Python programming and help them build a strong foundation in software development.",
        "learning_topics": [
            "Python fundamentals",
            "Variables and data types",
            "Conditions and loops",
            "Functions",
            "Data structures",
            "Modules and packages",
            "Object-oriented programming",
            "File handling",
            "Error handling",
            "Working with APIs",
            "Introduction to Git and GitHub",
            "Practical exercises",
            "Mini-project development",
        ],
        "learning_approach": [
            "Structured daily learning",
            "Practical exercises",
            "Community support",
            "Peer learning",
            "Assignments",
            "Mini-projects",
            "Progress tracking where applicable",
        ],
        "meta_title": "30 Days of Python | Python Togo",
        "meta_description": "Explore Python Togo's 30 Days of Python program, a structured introductory training pathway for beginners and learners building core programming skills.",
    },
    {
        "slug": "mentorship",
        "name": "Python Togo Mentorship Program",
        "url": "/programs/mentorship",
        "duration": "12 months",
        "type": "Long-term mentor–mentee development program",
        "audience": "Beginners, students, self-taught developers, early-career developers, and community members seeking growth",
        "focus": "Mentorship, peer programming, peer learning, technical growth, and project development",
        "certificate": "Certificate of Completion after successful completion of the mentorship cycle and its requirements.",
        "short_description": "A structured 12-month learning and development initiative that connects mentees with mentors to support personal growth, technical learning, and practical project work.",
        "description": "The Python Togo Mentorship Program is a structured 12-month learning and development initiative that connects mentees with mentors to support technical growth, peer collaboration, practical learning, and long-term professional development.",
        "learning_topics": [
            "Mentor–mentee pairing",
            "Peer programming",
            "Peer learning",
            "Technical growth",
            "Project-based learning",
            "Progress and accountability",
        ],
        "learning_approach": [
            "Guidance from mentors",
            "Collaborative coding and problem solving",
            "Knowledge-sharing sessions",
            "Study groups and discussions",
            "Feedback and follow-up",
            "Improvement of technical and professional skills",
        ],
        "meta_title": "Python Togo Mentorship Program",
        "meta_description": "Learn about Python Togo's 12-month mentorship program designed to support technical growth, peer collaboration, and practical learning.",
    },
    {
        "slug": "engineering-bootcamp",
        "name": "Python Togo Engineering Bootcamp",
        "url": "/programs/engineering-bootcamp",
        "duration": "6 months total (3 months foundation + 3 months practical training)",
        "type": "Structured software engineering pathway",
        "audience": "Aspiring developers, career changers, and learners ready for applied engineering work",
        "focus": "Python, software engineering, DevOps, cloud infrastructure, deployment, and specialization",
        "certificate": "Certificate of Completion or Certificate of Professional Training for participants who successfully complete the program requirements.",
        "short_description": "A six-month pathway from Python fundamentals to practical software engineering, deployment, and technical specialization.",
        "description": "The Python Togo Engineering Bootcamp is a structured six-month educational pathway that builds a strong common foundation in Python and software engineering before participants choose an area of specialization aligned with their interests and career goals.",
        "learning_topics": [
            "Python programming",
            "Programming fundamentals",
            "Software development principles",
            "Git and GitHub",
            "Linux fundamentals",
            "Databases",
            "APIs",
            "Testing",
            "Debugging",
            "Software architecture fundamentals",
            "Application development",
            "Deployment fundamentals",
            "DevOps fundamentals",
            "Cloud infrastructure fundamentals",
            "Team collaboration",
            "Project-based learning",
        ],
        "learning_approach": [
            "Practical projects",
            "Team-based development",
            "Real-world use cases",
            "Technical assignments",
            "Deployment activities",
            "Project documentation",
            "Collaboration workflows",
            "Guided practical experience",
        ],
        "meta_title": "Python Togo Engineering Bootcamp",
        "meta_description": "Discover Python Togo's six-month engineering bootcamp combining software fundamentals, practical experience, and specialization pathways.",
    },
]


@app.get("/programs", response_class=HTMLResponse)
async def programs(request: Request):
    """Render the educational programs overview page."""
    lang = get_language(request)
    return templates.TemplateResponse(
        request=request,
        name="programs.html",
        context=ctx(
            request,
            {
                "programs": PROGRAMS,
                "meta_title": "Python Togo Educational Programs — Python Togo",
                "meta_description": "Explore Python Togo's structured educational programs, including 30 Days of Python, mentorship, and a practical software engineering bootcamp.",
            },
        ),
    )


@app.get("/programs/30-days-of-python", response_class=HTMLResponse)
async def program_30_days_of_python(request: Request):
    """Render the 30 Days of Python detail page."""
    program = next(
        item for item in PROGRAMS if item["slug"] == "30-days-of-python")
    return templates.TemplateResponse(
        request=request,
        name="program_detail.html",
        context=ctx(
            request,
            {
                "program": program,
                "meta_title": program["meta_title"],
                "meta_description": program["meta_description"],
            },
        ),
    )


@app.get("/programs/mentorship", response_class=HTMLResponse)
async def program_mentorship(request: Request):
    """Render the mentorship detail page."""
    program = next(item for item in PROGRAMS if item["slug"] == "mentorship")
    return templates.TemplateResponse(
        request=request,
        name="program_detail.html",
        context=ctx(
            request,
            {
                "program": program,
                "meta_title": program["meta_title"],
                "meta_description": program["meta_description"],
            },
        ),
    )


@app.get("/programs/engineering-bootcamp", response_class=HTMLResponse)
async def program_engineering_bootcamp(request: Request):
    """Render the engineering bootcamp detail page."""
    program = next(
        item for item in PROGRAMS if item["slug"] == "engineering-bootcamp")
    return templates.TemplateResponse(
        request=request,
        name="program_detail.html",
        context=ctx(
            request,
            {
                "program": program,
                "meta_title": program["meta_title"],
                "meta_description": program["meta_description"],
            },
        ),
    )


@app.get("/education", response_class=HTMLResponse)
async def education(request: Request):
    """Render the education landing page for public institutional overview."""
    return templates.TemplateResponse(
        request=request,
        name="education.html",
        context=ctx(
            request,
            {
                "programs": PROGRAMS,
                "meta_title": "Education at Python Togo",
                "meta_description": "Python Togo provides community-driven technical education through structured programs, mentorship, practical training, and project-based learning.",
            },
        ),
    )


@app.get("/certificates", response_class=HTMLResponse)
async def certificates(request: Request):
    """Render the certificates overview page."""
    return templates.TemplateResponse(
        request=request,
        name="certificates.html",
        context=ctx(
            request,
            {
                "programs": PROGRAMS,
                "meta_title": "Python Togo Certificates",
                "meta_description": "Python Togo provides certificates of completion to participants who successfully fulfill the requirements of its structured educational programs.",
            },
        ),
    )


@app.get("/pythoberfest")
async def pythoberfest(request: Request):
    return RedirectResponse(url="https://events.mlh.com/events/15369-hacktoberfest-hack-day-lome-x-python-togo", status_code=302)


@app.get("/events")
async def events(request: Request):
    """
    Render the events listing page using sample events data.

    Parameters
    ----------
    request : fastapi.Request
        The incoming request.

    Returns
    -------
    fastapi.responses.HTMLResponse
        Rendered template response.

    Examples
    --------
    ``GET /events``
    """
    lang = get_language(request)
    items = []
    for e in EVENTS:
        tr = e.get("translations", {}).get(lang, {})
        items.append(
            {
                "id": e["id"],
                "date": e["date"],
                "location": e.get("location", ""),
                "image": e.get("image", "https://ik.imagekit.io/foscyymdh/pythontogo/Banni%C3%A8res%20YouTube%20-%20Python%20Software%20Community%20(1).png"),
                "link": e.get("link", "https://www.pytogo.org/"),
                "title": tr.get("title", ""),
                "description": tr.get("description", ""),
            }
        )
    items = sorted(items, key=lambda x: x["date"], reverse=True)
    return templates.TemplateResponse(
        request=request,
        name="events.html",
        context=ctx(
            request,
            {
                "events": items,
                "meta_title": TRANSLATIONS[lang]["events-title"] + " — Python Togo",
                "meta_description": TRANSLATIONS[lang]["events-sample-desc"],
            },
        ),
    )


@app.get("/events/{event_id}")
async def event_detail(event_id: int, request: Request):
    """
    Render a single event page.

    Parameters
    ----------
    event_id : int
        Identifier of the event to display.
    request : fastapi.Request
        The incoming request.

    Returns
    -------
    fastapi.responses.HTMLResponse
        Rendered template response.

    Examples
    --------
    ``GET /events/1``
    """
    lang = get_language(request)
    found = next((e for e in EVENTS if e["id"] == event_id), None)
    if not found:
        raise HTTPException(status_code=404, detail="Event not found")
    tr = found.get("translations", {}).get(lang, {})
    item = {
        "id": found["id"],
        "date": found["date"],
        "location": found.get("location", ""),
        "title": tr.get("title", ""),
        "description": tr.get("description", ""),
    }
    return templates.TemplateResponse(
        request=request,
        name="event_detail.html",
        context=ctx(
            request,
            {
                "item": item,
                "meta_title": item["title"] + " — Python Togo",
                "meta_description": item["description"],
            },
        ),
    )


@app.get("/actualities")
async def actualities(request: Request):
    """
    Render the news (actualities) listing page.

    Parameters
    ----------
    request : fastapi.Request
        The incoming request.

    Returns
    -------
    fastapi.responses.HTMLResponse
        Rendered template response.

    Examples
    --------
    ``GET /actualities``
    """
    lang = get_language(request)
    items = []
    for n in NEWS:
        tr = n.get("translations", {}).get(lang, {})
        img = n.get(
            "image") or f"https://picsum.photos/seed/news-{n['id']}/600/340"
        items.append(
            {
                "id": n["id"],
                "date": n["date"],
                "title": tr.get("title", ""),
                "excerpt": tr.get("excerpt", ""),
                "image": img,
            }
        )
    return templates.TemplateResponse(
        request=request,
        name="actualites.html",
        context=ctx(
            request,
            {
                "news": items,
                "meta_title": TRANSLATIONS[lang]["news-title"] + " — Python Togo",
                "meta_description": TRANSLATIONS[lang]["footer-about-desc"],
            },
        ),
    )


@app.get("/actualities/{news_id}")
async def news_detail(news_id: int, request: Request):
    """
    Render a single news page.

    Parameters
    ----------
    news_id : int
        Identifier of the news item.
    request : fastapi.Request
        The incoming request.

    Returns
    -------
    fastapi.responses.HTMLResponse
        Rendered template response.

    Examples
    --------
    ``GET /actualities/2``
    """
    lang = get_language(request)
    found = next((n for n in NEWS if n["id"] == news_id), None)
    if not found:
        raise HTTPException(status_code=404, detail="News not found")
    tr = found.get("translations", {}).get(lang, {})
    item = {
        "id": found["id"],
        "date": found["date"],
        "title": tr.get("title", ""),
        "body": tr.get("body", ""),
        "image": found.get("image")
        or f"https://picsum.photos/seed/news-{found['id']}/1200/680",
    }
    return templates.TemplateResponse(
        request=request,
        name="news_detail.html",
        context=ctx(
            request,
            {
                "item": item,
                "meta_title": item["title"] + " — Python Togo",
                "meta_description": item["body"][:160],
                "meta_image": item.get("image"),
            },
        ),
    )


@app.get("/partners")
async def partners(request: Request):
    """
    Render the partners page.

    Parameters
    ----------
    request : fastapi.Request
        The incoming request.

    Returns
    -------
    fastapi.responses.HTMLResponse
        Rendered template response.
    """
    lang = get_language(request)
    return templates.TemplateResponse(
        request=request,
        name="partners.html",
        context=ctx(
            request,
            {
                "partners": PARTNERS,
                "meta_title": TRANSLATIONS[lang]["nav-partners"] + " — Python Togo",
                "meta_description": TRANSLATIONS[lang]["partners-intro"],
            },
        ),
    )


@app.get("/communities")
async def communities(request: Request):
    """
    Render the communities page.

    Parameters
    ----------
    request : fastapi.Request
        The incoming request.

    Returns
    -------
    fastapi.responses.HTMLResponse
        Rendered template response.
    """
    lang = get_language(request)
    return templates.TemplateResponse(
        request=request,
        name="communities.html",
        context=ctx(
            request,
            {
                "meta_title": TRANSLATIONS[lang]["nav-communities"] + " — Python Togo",
                "meta_description": TRANSLATIONS[lang]["communities-card-desc"],
            },
        ),
    )


@app.get("/join")
async def join(request: Request):
    """
    Render the join page (membership form).

    Parameters
    ----------
    request : fastapi.Request
        The incoming request.

    Returns
    -------
    fastapi.responses.HTMLResponse
        Rendered template response.
    """
    lang = get_language(request)
    return templates.TemplateResponse(
        request=request,
        name="join.html",
        context=ctx(
            request,
            {
                "meta_title": TRANSLATIONS[lang]["join-title"] + " — Python Togo",
                "meta_description": TRANSLATIONS[lang]["join-intro"],
            },
        ),
    )


@app.get("/contact")
async def contact(request: Request):
    """
    Render the contact page (contact form).

    Parameters
    ----------
    request : fastapi.Request
        The incoming request.

    Returns
    -------
    fastapi.responses.HTMLResponse
        Rendered template response.
    """
    lang = get_language(request)
    return templates.TemplateResponse(
        request=request,
        name="contact.html",
        context=ctx(
            request,
            {
                "meta_title": TRANSLATIONS[lang]["contact-title"] + " — Python Togo",
                "meta_description": TRANSLATIONS[lang]["contact-intro"],
            },
        ),
    )


@app.get("/code-of-conduct")
async def code_of_conduct(request: Request):
    """
    Render the Code of Conduct page.

    Parameters
    ----------
    request : fastapi.Request
        The incoming request.

    Returns
    -------
    fastapi.responses.HTMLResponse
        Rendered template response.
    """
    lang = get_language(request)
    return templates.TemplateResponse(
        request=request,
        name="code_of_conduct.html",
        context=ctx(
            request,
            {
                "meta_title": TRANSLATIONS[lang]["coc-title"] + " — Python Togo",
                "meta_description": TRANSLATIONS[lang]["coc-intro"],
            },
        ),
    )


@app.post("/api/v1/partnership")
async def partnership_submit(request: Request):
    """
    Receive partnership form submissions as JSON.

    Parameters
    ----------
    request : fastapi.Request
        The incoming request (JSON or form).

    Returns
    -------
    fastapi.responses.JSONResponse
        Status indicating receipt of the request.
    """
    ct = request.headers.get("content-type", "")
    if "application/json" in ct:
        payload = await request.json()
    else:
        form = await request.form()
        payload = dict(form)

    print(f"Partnership payload: {payload}")

    data = PartnershipRequest(**payload)

    print(data)
    try:
        validate_email(data.email, check_deliverability=True)
    except EmailNotValidError:
        return JSONResponse(
            status_code=400, content={"error": "Please use a valid email"}
        )

    # Normalize boolean fields (coerce possible string values)
    agree_privacy = getattr(data, "agree_privacy", False) in (
        True,
        "true",
        "True",
        "on",
        "1",
        1,
    )
    agree_coc = getattr(data, "agree_coc", False) in (
        True,
        "true",
        "True",
        "on",
        "1",
        1,
    )
    if not agree_privacy or not agree_coc:
        return JSONResponse(status_code=400, content={"error": "consent_required"})

    inserted = insert_data("partnershiprequest", data.dict())
    if inserted:
        return JSONResponse(content={"status": "received"})
    else:
        return JSONResponse(content={"status": "Failed"})


@app.post("/api/v1/join")
async def join_submit(request: Request):
    """
    Receive join form submissions (JSON or form-encoded).

    Requires consent checkboxes to be set; otherwise returns 400.

    Parameters
    ----------
    request : fastapi.Request
        The incoming request containing form or JSON payload.

    Returns
    -------
    fastapi.responses.JSONResponse
        Status indicating receipt of the request, or 400 on consent missing.
    """
    ct = request.headers.get("content-type", "")
    if "application/json" in ct:
        payload = await request.json()
    else:
        form = await request.form()
        payload = dict(form)

    data = JoinRequest(**payload)

    try:
        validate_email(data.email, check_deliverability=True)
    except EmailNotValidError:
        return JSONResponse(
            status_code=400, content={"error": "Please use a valid email"}
        )

    # Normalize boolean fields
    agree_privacy = getattr(data, "agree_privacy", False) in (
        True,
        "true",
        "True",
        "on",
        "1",
        1,
    )
    agree_coc = getattr(data, "agree_coc", False) in (
        True,
        "true",
        "True",
        "on",
        "1",
        1,
    )
    if not agree_privacy or not agree_coc:
        return JSONResponse(status_code=400, content={"error": "consent_required"})

    inserted = insert_data("members", data.dict())
    if inserted:
        return JSONResponse(content={"status": "received"})
    else:
        return JSONResponse(content={"status": "Failed"})


@app.post("/api/v1/contact")
async def contact_submit(request: Request):
    """
    Receive contact form submissions (JSON or form-encoded).

    Requires consent checkboxes to be set; otherwise returns 400.

    Parameters
    ----------
    request : fastapi.Request
        The incoming request containing form or JSON payload.

    Returns
    -------
    fastapi.responses.JSONResponse
        Status indicating receipt of the message, or 400 on consent missing.
    """
    ct = request.headers.get("content-type", "")
    if "application/json" in ct:
        payload = await request.json()
    else:
        form = await request.form()
        payload = dict(form)

    data = ContactSubmit(**payload)

    try:
        validate_email(data.email, check_deliverability=True)
    except EmailNotValidError:
        return JSONResponse(
            status_code=400, content={"error": "Please use a valid email"}
        )

    agree_privacy = getattr(data, "agree_privacy", False) in (
        True,
        "true",
        "True",
        "on",
        "1",
        1,
    )
    agree_coc = getattr(data, "agree_coc", False) in (
        True,
        "true",
        "True",
        "on",
        "1",
        1,
    )
    if not agree_privacy or not agree_coc:
        return JSONResponse(status_code=400, content={"error": "consent_required"})

    inserted = insert_data("contacts", data.dict())
    if inserted:
        return JSONResponse(content={"status": "received"})
    else:
        return JSONResponse(content={"status": "Failed"})


@app.get("/gallery")
async def gallery(request: Request):
    """
    Render the gallery page with external links.

    Parameters
    ----------
    request : fastapi.Request
        The incoming request.

    Returns
    -------
    fastapi.responses.HTMLResponse
        Rendered template response.
    """
    return templates.TemplateResponse(
        request=request,
        name="gallery.html",
        context=ctx(request, {"galleries": GALLERIES}),
    )


@app.get("/privacy")
async def privacy(request: Request):
    """
    Render the privacy policy page.

    Parameters
    ----------
    request : fastapi.Request
        The incoming request.

    Returns
    -------
    fastapi.responses.HTMLResponse
        Rendered template response.
    """
    lang = get_language(request)
    return templates.TemplateResponse(
        request=request,
        name="privacy.html",
        context=ctx(
            request,
            {
                "meta_title": TRANSLATIONS[lang]["privacy-title"] + " — Python Togo",
                "meta_description": TRANSLATIONS[lang]["privacy-intro"],
            },
        ),
    )


# redirections

app.get("/favicon.ico")(lambda: RedirectResponse(url="/static/images/Py.png"))
app.get("/discord")(
    lambda: RedirectResponse(
        url="https://discord.gg/RP76qhwrNY", status_code=301)
)
app.get("/linkedin")(
    lambda: RedirectResponse(
        url="https://www.linkedin.com/company/pythontogo/", status_code=301
    )
)
app.get("/twitter")(
    lambda: RedirectResponse(url="https://x.com/pytogo_org", status_code=301)
)
app.get("/x")(lambda: RedirectResponse(url="https://x.com/pytogo_org", status_code=301))
app.get("/instagram")(
    lambda: RedirectResponse(
        url="https://www.instagram.com/pycontg/", status_code=301)
)
app.get("/x")(lambda: RedirectResponse(url="https://x.com/pytogo_org", status_code=301))
app.get("/facebook")(
    lambda: RedirectResponse(
        url="https://www.facebook.com/share/1DA5jFdhbp/", status_code=301
    )
)
app.get("/mastodon")(
    lambda: RedirectResponse(
        url="https://techhub.social/@pytogo_org", status_code=301)
)
app.get("/meet")(
    lambda: RedirectResponse(
        url="https://meet.google.com/mnt-zerh-oqw", status_code=301
    )
)
app.get("/github")(
    lambda: RedirectResponse(
        url="https://github.com/python-togo", status_code=301)
)
app.get("/youtube")(
    lambda: RedirectResponse(
        url="https://www.youtube.com/@PythonTogo", status_code=301)
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8080)
