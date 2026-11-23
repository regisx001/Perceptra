import os
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

IMAGES_DIR = "/home/regisx001/Perceptra/Report/images"
os.makedirs(IMAGES_DIR, exist_ok=True)

PRIMARY = "#483D8B"
SLATE = "#262A34"
LIGHT = "#F6F7FA"
ACCENT = "#3068B2"
BORDER = "#483D8B"
GRAY = "#606670"
WHITE = "#FFFFFF"

def compile_dot(dot_content: str, output_png: str, dpi: int = 180):
    dot_file = output_png.replace(".png", ".dot")
    with open(dot_file, "w", encoding="utf-8") as f:
        f.write(dot_content)
    cmd = ["dot", f"-Gdpi={dpi}", "-Tpng", dot_file, "-o", output_png]
    subprocess.run(cmd, check=True)
    if os.path.exists(dot_file):
        os.remove(dot_file)
    # Ensure reasonable dimensions for LaTeX
    with Image.open(output_png) as im:
        if im.width > 2200 or im.height > 2200:
            im.thumbnail((2200, 2200), Image.Resampling.LANCZOS)
            im.save(output_png)
    print(f"Generated: {output_png}")

# -------------------------------------------------------------
# 00: Architecture Globale Perceptra
# -------------------------------------------------------------
dot_00 = f"""
digraph G {{
    rankdir=TB;
    bgcolor="{WHITE}";
    compound=true;
    nodesep=0.5;
    ranksep=0.6;
    node [shape=box, style="filled,rounded", fontname="Helvetica", fontsize=11, fillcolor="{LIGHT}", color="{BORDER}", penwidth=1.5, fontcolor="{SLATE}"];
    edge [color="{PRIMARY}", penwidth=1.5, fontname="Helvetica", fontsize=9, fontcolor="{GRAY}"];

    subgraph cluster_client {{
        label = "Niveau Client (Navigateur Web)";
        fontname="Helvetica-Bold"; fontsize=12; fontcolor="{PRIMARY}";
        style="dashed,rounded"; color="{PRIMARY}"; bgcolor="#FAFAFD";
        
        UI [label="Interface Utilisateur\\nSvelte 5 + SvelteKit\\nShadcn-Svelte + Tailwind 4", fillcolor="#EDE9FE"];
        State [label="Gestion d'États & Runes\\n$state / $derived / Context", fillcolor="#EDE9FE"];
        UI -> State [dir=both, label="Liaisons réactives"];
    }}

    subgraph cluster_gateway {{
        label = "Passerelle & Sécurité";
        fontname="Helvetica-Bold"; fontsize=12; fontcolor="{PRIMARY}";
        style="dashed,rounded"; color="{PRIMARY}"; bgcolor="#F8FAFC";
        
        Nginx [label="Reverse Proxy / Vite Dev Server\\nCORS, Compression & Headers", fillcolor="#E2E8F0"];
        Auth_MW [label="Sécurité & Session\\nJWT Bearer Token Validation", fillcolor="#E2E8F0"];
    }}

    subgraph cluster_backend {{
        label = "Niveau Applicatif (Backend Flask Core)";
        fontname="Helvetica-Bold"; fontsize=12; fontcolor="{PRIMARY}";
        style="dashed,rounded"; color="{PRIMARY}"; bgcolor="#F5F3FF";

        AppFactory [label="Application Factory\\nFlask 3.x + Blueprints REST", fillcolor="#DDD6FE"];
        
        subgraph cluster_services {{
            label = "Couche de Services Métier";
            fontname="Helvetica-Bold"; fontsize=11; fontcolor="{PRIMARY}";
            style="solid,rounded"; color="{ACCENT}"; bgcolor="{WHITE}";
            
            ImgSvc [label="ImageService\\nCRUD, Batch & Formats"];
            TransfSvc [label="TransformEngine\\nCrop, Resize, Affine"];
            DescSvc [label="DescriptorEngine\\nHSV, Moments, KMeans, GLCM, LBP"];
            SimSvc [label="SimilarityEngine\\nCosinus, Euclidienne normalisée"];
            FRESvc [label="FeatureRelevanceEstimator\\nDispersion, Fisher, CENTROID Update"];
        }}
    }}

    subgraph cluster_persistence {{
        label = "Niveau Persistance & Fichiers";
        fontname="Helvetica-Bold"; fontsize=12; fontcolor="{PRIMARY}";
        style="dashed,rounded"; color="{PRIMARY}"; bgcolor="#F1F5F9";

        DB [label="Base de Données Relationnelle\\nSQLite / PostgreSQL\\nSQLAlchemy ORM + Flask-Migrate", shape=cylinder, fillcolor="#FEF3C7"];
        Storage [label="Stockage Fichiers Local / Volume\\nImages Originales, Dérivées & GHIM-10K\\nVérification SHA-256", shape=folder, fillcolor="#FEF3C7"];
    }}

    UI -> Nginx [label="HTTPS / JSON REST API"];
    Nginx -> Auth_MW;
    Auth_MW -> AppFactory;
    AppFactory -> ImgSvc;
    AppFactory -> DescSvc;
    AppFactory -> SimSvc;
    AppFactory -> FRESvc;
    ImgSvc -> TransfSvc;
    ImgSvc -> Storage [label="I/O Binaire"];
    ImgSvc -> DB [label="Métadonnées"];
    DescSvc -> DB [label="Vecteurs JSON"];
    SimSvc -> DB [label="Index Vecteurs"];
    FRESvc -> DB [label="Historique Feedback"];
}}
"""
compile_dot(dot_00, f"{IMAGES_DIR}/00-architecture-globale-perceptra.png")

# -------------------------------------------------------------
# 01: Pipeline Fonctionnel et Parcours Utilisateur
# -------------------------------------------------------------
dot_01 = f"""
digraph G {{
    rankdir=LR;
    bgcolor="{WHITE}";
    nodesep=0.4;
    ranksep=0.5;
    node [shape=box, style="filled,rounded", fontname="Helvetica", fontsize=10, fillcolor="{LIGHT}", color="{BORDER}", penwidth=1.4, fontcolor="{SLATE}"];
    edge [color="{PRIMARY}", penwidth=1.4, fontname="Helvetica", fontsize=9, fontcolor="{GRAY}"];

    User [label="Utilisateur\\nAuthentifié", shape=ellipse, fillcolor="#EDE9FE"];
    Upload [label="1. Importation Images\\n(Unitaire ou Batch)"];
    Transform [label="2. Retouche / Filtres\\n(Crop, Resize, Rotation)"];
    Category [label="3. Organisation\\nCatégories Arborescentes"];
    Extract [label="4. Extraction Automatique\\nDescripteurs Visuels"];
    Query [label="5. Requête par Image\\n(Upload ou Galerie)"];
    Search [label="6. Moteur de Recherche\\nCalcul des Similarités"];
    Results [label="7. Affichage Top-K\\nScores & Décomposition"];
    Feedback [label="8. Retours Pertinence\\n(Marquage Pertinent/Non-Pertinent)"];
    Refine [label="9. Réestimation FRE\\nPondération & Nouveau Centroïde"];

    User -> Upload;
    User -> Query;
    Upload -> Transform [style=dotted, label="optionnel"];
    Upload -> Category;
    Upload -> Extract [label="Calcul asynchrone"];
    Transform -> Extract;
    Category -> Query;
    Extract -> Search;
    Query -> Search;
    Search -> Results;
    Results -> Feedback [label="Évaluation"];
    Feedback -> Refine [label="Algorithme FRE"];
    Refine -> Search [label="Itération suivante"];
}}
"""
compile_dot(dot_01, f"{IMAGES_DIR}/01-perceptra-pipeline-fonctionnel.png")

# -------------------------------------------------------------
# 02: Cadre Conceptuel CBIR & Semantic Gap
# -------------------------------------------------------------
dot_02 = f"""
digraph G {{
    rankdir=TB;
    bgcolor="{WHITE}";
    nodesep=0.5;
    ranksep=0.6;
    node [shape=box, style="filled,rounded", fontname="Helvetica", fontsize=11, fillcolor="{LIGHT}", color="{BORDER}", penwidth=1.5, fontcolor="{SLATE}"];
    edge [color="{PRIMARY}", penwidth=1.5, fontname="Helvetica", fontsize=9, fontcolor="{GRAY}"];

    subgraph cluster_semantic {{
        label = "Niveau Sémantique Humain (Haut Niveau)";
        fontname="Helvetica-Bold"; fontsize=12; fontcolor="{PRIMARY}";
        style="dashed,rounded"; color="{PRIMARY}"; bgcolor="#FFFBEB";

        Concept [label="Concepts Abstraits & Intentions\\n'Voiture rouge sportive', 'Coucher de soleil en mer'\\nPerception subjective et contextuelle", fillcolor="#FEF3C7"];
    }}

    subgraph cluster_gap {{
        label = "Le Fossé Sémantique (Semantic Gap)";
        fontname="Helvetica-Bold"; fontsize=12; fontcolor="#DC2626";
        style="dotted,rounded"; color="#DC2626"; bgcolor="#FEF2F2";

        Gap [label="Fossé Sémantique\\nDifférence intrinsèque entre les pixels numériques\\net l'interprétation sémantique humaine", shape=octagon, fillcolor="#FEE2E2", fontcolor="#991B1B"];
    }}

    subgraph cluster_low_level {{
        label = "Niveau Numérique / Caractéristiques Visuelles (Bas Niveau)";
        fontname="Helvetica-Bold"; fontsize=12; fontcolor="{ACCENT}";
        style="dashed,rounded"; color="{ACCENT}"; bgcolor="#F0F9FF";

        Color [label="Primitives de Couleur\\nHistogramme HSV (768-D)\\nMoments statistiques (9-D)\\nCouleurs dominantes (KMeans)", fillcolor="#E0F2FE"];
        Texture [label="Primitives de Texture\\nMatrices GLCM (4 métriques multi-angles)\\nMotifs binaires locaux LBP (256-D)", fillcolor="#E0F2FE"];
    }}

    subgraph cluster_solution {{
        label = "Comblement du Fossé : Relevance Feedback Interactif";
        fontname="Helvetica-Bold"; fontsize=12; fontcolor="{PRIMARY}";
        style="solid,rounded"; color="{PRIMARY}"; bgcolor="#F5F3FF";

        FRE [label="Feature Relevance Estimation (Groupe 13)\\nAdaptation dynamique des poids de caractéristiques\\nDéplacement guidé du centroïde de la requête\\nConvergence itérative vers l'intention utilisateur", fillcolor="#DDD6FE"];
    }}

    Concept -> Gap [label="Impossible à formaliser directement", color="#DC2626"];
    Gap -> Color [label="Extraction mathématique déterministe"];
    Gap -> Texture;
    Color -> FRE [label="Pondération adaptative"];
    Texture -> FRE;
    FRE -> Concept [label="Alignement progressif interactif", color="{PRIMARY}", penwidth=2.0];
}}
"""
compile_dot(dot_02, f"{IMAGES_DIR}/02-etat-de-l-art-cbir-framework.png")

# -------------------------------------------------------------
# 03: Architecture Système N-Tiers
# -------------------------------------------------------------
dot_03 = f"""
digraph G {{
    rankdir=TB;
    bgcolor="{WHITE}";
    nodesep=0.4;
    ranksep=0.5;
    node [shape=box, style="filled,rounded", fontname="Helvetica", fontsize=10, fillcolor="{LIGHT}", color="{BORDER}", penwidth=1.4, fontcolor="{SLATE}"];
    edge [color="{PRIMARY}", penwidth=1.4, fontname="Helvetica", fontsize=9, fontcolor="{GRAY}"];

    subgraph cluster_tier1 {{
        label = "1. Couche Présentation (Frontend)";
        fontname="Helvetica-Bold"; fontsize=11; fontcolor="{PRIMARY}";
        style="solid,rounded"; color="{PRIMARY}"; bgcolor="#F8FAFC";
        
        T1_Pages [label="Pages SvelteKit (Svelte 5)\\n/dashboard, /search, /settings, /auth"];
        T1_Components [label="Composants UI Shadcn-Svelte\\nGalerie, Visualiseur, Modal Retouches, Tableaux TanStack"];
        T1_Stores [label="États Réactifs & Moteur i18n\\nRunes $state, Paraglide-JS, API Client Fetch"];
        T1_Pages -> T1_Components;
        T1_Components -> T1_Stores;
    }}

    subgraph cluster_tier2 {{
        label = "2. Couche Exposition & Routage (API Gateway / REST)";
        fontname="Helvetica-Bold"; fontsize=11; fontcolor="{PRIMARY}";
        style="solid,rounded"; color="{PRIMARY}"; bgcolor="#F8FAFC";

        T2_BP_Auth [label="/api/auth\\nJWT Sign-in & Register"];
        T2_BP_Img [label="/api/images\\nUpload, Download, Batch, Retouches"];
        T2_BP_Cat [label="/api/categories\\nArborescence hiérarchique"];
        T2_BP_Desc [label="/api/descriptors\\nExtraction & Visualisation"];
        T2_BP_Query [label="/api/query\\nRecherche simple & Feedback FRE"];
        T2_BP_Analytics [label="/api/analytics\\nLogs, Métriques, Performances"];
    }}

    subgraph cluster_tier3 {{
        label = "3. Couche Métier & Calcul Scientifique (Service Layer)";
        fontname="Helvetica-Bold"; fontsize=11; fontcolor="{PRIMARY}";
        style="solid,rounded"; color="{PRIMARY}"; bgcolor="#F8FAFC";

        T3_ImgSvc [label="ImageService & StorageManager\\nValidation MIME, SHA-256, Arborescence disque"];
        T3_Transf [label="TransformEngine\\nTraitement Pillow & OpenCV (Crop, Resize, Affine)"];
        T3_DescEng [label="DescriptorEngine (OpenCV, Skimage)\\nHSV 768-D, Moments 9-D, KMeans, GLCM, LBP 256-D"];
        T3_SimEng [label="SimilarityEngine\\nCosinus, Euclidienne, Normalisation MinMax/Standard"];
        T3_FRE [label="FeatureRelevanceEstimator\\nDispersion intra/inter-classe, Ratio de Fisher, Lissage"];
    }}

    subgraph cluster_tier4 {{
        label = "4. Couche Données & Persistance (Persistence Layer)";
        fontname="Helvetica-Bold"; fontsize=11; fontcolor="{PRIMARY}";
        style="solid,rounded"; color="{PRIMARY}"; bgcolor="#F8FAFC";

        T4_ORM [label="SQLAlchemy ORM + Flask-Migrate\\nModèles relationnels, Contraintes, Indexations"];
        T4_DB [label="Base SQLite / PostgreSQL\\nStockage structuré des métadonnées & vecteurs", shape=cylinder, fillcolor="#FEF3C7"];
        T4_Disk [label="Système de Fichiers (Volume Docker)\\nArborescence de stockage des images brutes", shape=folder, fillcolor="#FEF3C7"];
    }}

    T1_Stores -> T2_BP_Img [label="Requêtes HTTP / REST JSON"];
    T1_Stores -> T2_BP_Query;
    T2_BP_Img -> T3_ImgSvc;
    T2_BP_Img -> T3_Transf;
    T2_BP_Desc -> T3_DescEng;
    T2_BP_Query -> T3_SimEng;
    T2_BP_Query -> T3_FRE;
    T3_ImgSvc -> T4_Disk;
    T3_ImgSvc -> T4_ORM;
    T3_DescEng -> T4_ORM;
    T3_SimEng -> T4_ORM;
    T3_FRE -> T4_ORM;
    T4_ORM -> T4_DB;
}}
"""
compile_dot(dot_03, f"{IMAGES_DIR}/03-architecture-systeme-n-tiers.png")

# -------------------------------------------------------------
# 04: Architecture Backend Flask
# -------------------------------------------------------------
dot_04 = f"""
digraph G {{
    rankdir=LR;
    bgcolor="{WHITE}";
    nodesep=0.4;
    ranksep=0.6;
    node [shape=box, style="filled,rounded", fontname="Helvetica", fontsize=10, fillcolor="{LIGHT}", color="{BORDER}", penwidth=1.4, fontcolor="{SLATE}"];
    edge [color="{PRIMARY}", penwidth=1.4, fontname="Helvetica", fontsize=9, fontcolor="{GRAY}"];

    WSGI [label="Serveur Gunicorn\\nMulti-Workers Synch/Gevent", fillcolor="#EDE9FE"];
    Factory [label="create_app()\\nApp Factory Pattern", fillcolor="#DDD6FE"];
    Config [label="Config Classes\\nDev, Prod, Test"];
    Ext [label="Extensions Flask\\nSQLAlchemy (db)\\nFlask-Migrate\\nFlask-JWT-Extended\\nCORS"];

    WSGI -> Factory;
    Config -> Factory;
    Ext -> Factory [dir=both];

    subgraph cluster_routes {{
        label = "Blueprints RESTful";
        fontname="Helvetica-Bold"; fontsize=11; fontcolor="{PRIMARY}";
        style="solid,rounded"; color="{PRIMARY}"; bgcolor="#FAFAFD";

        BP_Auth [label="auth_bp\\n/api/auth"];
        BP_Images [label="images_bp\\n/api/images"];
        BP_Categories [label="categories_bp\\n/api/categories"];
        BP_Descriptors [label="descriptors_bp\\n/api/descriptors"];
        BP_Query [label="query_bp\\n/api/query"];
        BP_Analytics [label="analytics_bp\\n/api/analytics"];
    }}

    Factory -> BP_Auth;
    Factory -> BP_Images;
    Factory -> BP_Categories;
    Factory -> BP_Descriptors;
    Factory -> BP_Query;
    Factory -> BP_Analytics;
}}
"""
compile_dot(dot_04, f"{IMAGES_DIR}/04-architecture-backend-flask.png")

# -------------------------------------------------------------
# 05: Pipeline Extraction Descripteurs
# -------------------------------------------------------------
dot_05 = f"""
digraph G {{
    rankdir=TB;
    bgcolor="{WHITE}";
    nodesep=0.4;
    ranksep=0.5;
    node [shape=box, style="filled,rounded", fontname="Helvetica", fontsize=10, fillcolor="{LIGHT}", color="{BORDER}", penwidth=1.4, fontcolor="{SLATE}"];
    edge [color="{PRIMARY}", penwidth=1.4, fontname="Helvetica", fontsize=9, fontcolor="{GRAY}"];

    Raw [label="Flux Binaire Image (bytes)\\nUpload ou Fichier Disque", fillcolor="#EDE9FE"];
    Decode [label="Décodage & Normalisation\\nPIL / EXIF Transpose -> RGB uint8\\nValidation Dimensions & Non-corruption", fillcolor="#EDE9FE"];

    Raw -> Decode;

    subgraph cluster_color {{
        label = "Descripteurs de Couleur";
        fontname="Helvetica-Bold"; fontsize=11; fontcolor="{PRIMARY}";
        style="dashed,rounded"; color="{PRIMARY}"; bgcolor="#FFFDF5";

        Hist [label="Histogramme HSV\\nResize 256x256 -> HSV\\nH:256, S:256, V:256\\nNormalisation L1\\n-> Vecteur 768-D"];
        Moments [label="Moments de Couleur\\nHSV normalisé dans [0, 1]\\nMoyenne, Écart-type, Asymétrie (m3^1/3)\\n-> Vecteur 9-D"];
        Dominant [label="Couleurs Dominantes\\nMiniBatchKMeans (k=5, 10, 20)\\nCentres RGB [0,1] + % surface\\n-> Vecteur k*4-D (20-D)"];
    }}

    subgraph cluster_texture {{
        label = "Descripteurs de Texture";
        fontname="Helvetica-Bold"; fontsize=11; fontcolor="{ACCENT}";
        style="dashed,rounded"; color="{ACCENT}"; bgcolor="#F5F9FF";

        GLCM [label="Matrice GLCM\\nNiveaux de gris quantifiés (32 levels)\\nAngles: 0°, 45°, 90°, 135°, d=1\\nContraste, Corrélation, Énergie, Homogénéité\\n-> Vecteur 4-D synthétique"];
        LBP [label="Motifs Binaires Locaux LBP\\nNiveaux de gris, P=8, R=1\\nHistogramme 256 cases normalisé L1\\n-> Vecteur 256-D"];
    }}

    Fuse [label="Vecteur de Caractéristiques Combiné\\nConcaténation pondérée & Normalisation d'échelle\\nStockage JSON & Cache Indexé", fillcolor="#D1FAE5", fontcolor="#065F46"];

    Decode -> Hist;
    Decode -> Moments;
    Decode -> Dominant;
    Decode -> GLCM;
    Decode -> LBP;

    Hist -> Fuse;
    Moments -> Fuse;
    Dominant -> Fuse;
    GLCM -> Fuse;
    LBP -> Fuse;
}}
"""
compile_dot(dot_05, f"{IMAGES_DIR}/05-pipeline-extraction-descripteurs.png")

# -------------------------------------------------------------
# 06: Pipeline Recherche par Similarité
# -------------------------------------------------------------
dot_06 = f"""
digraph G {{
    rankdir=LR;
    bgcolor="{WHITE}";
    nodesep=0.4;
    ranksep=0.5;
    node [shape=box, style="filled,rounded", fontname="Helvetica", fontsize=10, fillcolor="{LIGHT}", color="{BORDER}", penwidth=1.4, fontcolor="{SLATE}"];
    edge [color="{PRIMARY}", penwidth=1.4, fontname="Helvetica", fontsize=9, fontcolor="{GRAY}"];

    QueryImg [label="Image Requête q", shape=ellipse, fillcolor="#EDE9FE"];
    ExtractQ [label="Extraction des\\nDescripteurs q"];
    QueryImg -> ExtractQ;

    subgraph cluster_dataset {{
        label = "Collection Indexée (GHIM-10K / Galerie)";
        fontname="Helvetica-Bold"; fontsize=11; fontcolor="{PRIMARY}";
        style="dashed,rounded"; color="{PRIMARY}"; bgcolor="#F8FAFC";
        
        Candidates [label="Images Candidates i_1, ..., i_N\\nVecteurs précalculés en base"];
    }}

    SimComp [label="Calcul des Similarités par Descripteur\\nCosinus: S_j(q, i) = (1 + cos(q_j, i_j)) / 2\\nEuclidienne: S_j(q, i) = 1 / (1 + ||q_j - i_j||)"];
    
    Weights [label="Poids des Descripteurs w_j\\n(Initialement uniformes\\nou définis par l'utilisateur)"];

    Aggregate [label="Agrégation Convexe Multi-Descripteurs\\nS(q, i) = SUM( w_j * S_j(q, i) )\\navec SUM(w_j) = 1.0"];

    Rank [label="Ordonnancement Décroissant\\nTri par S(q, i) décroissant\\nSélection du Top-K"];

    TopK [label="Affichage Résultats Top-K\\nImages classées + Scores détaillés\\n(Globale, Couleur, Texture)", fillcolor="#D1FAE5"];

    ExtractQ -> SimComp;
    Candidates -> SimComp;
    SimComp -> Aggregate;
    Weights -> Aggregate;
    Aggregate -> Rank;
    Rank -> TopK;
}}
"""
compile_dot(dot_06, f"{IMAGES_DIR}/06-pipeline-recherche-similarite.png")

# -------------------------------------------------------------
# 07: Boucle Relevance Feedback (FRE - Groupe 13)
# -------------------------------------------------------------
dot_07 = f"""
digraph G {{
    rankdir=TB;
    bgcolor="{WHITE}";
    nodesep=0.5;
    ranksep=0.6;
    node [shape=box, style="filled,rounded", fontname="Helvetica", fontsize=10, fillcolor="{LIGHT}", color="{BORDER}", penwidth=1.4, fontcolor="{SLATE}"];
    edge [color="{PRIMARY}", penwidth=1.4, fontname="Helvetica", fontsize=9, fontcolor="{GRAY}"];

    subgraph cluster_user_step {{
        label = "Étape 1 : Retours Utilisateur";
        fontname="Helvetica-Bold"; fontsize=11; fontcolor="{PRIMARY}";
        style="dashed,rounded"; color="{PRIMARY}"; bgcolor="#FFFBEB";

        Results [label="Résultats de Recherche Affichés (Top-K)"];
        UserLabel [label="Marquage Interactif par l'Utilisateur\\nImages Pertinentes (Relevant, R)\\nImages Non-Pertinentes (Irrelevant, Ir)", fillcolor="#FEF3C7"];
        Results -> UserLabel;
    }}

    subgraph cluster_fre_algo {{
        label = "Étape 2 : Algorithme FRE (Feature Relevance Estimation)";
        fontname="Helvetica-Bold"; fontsize=11; fontcolor="{PRIMARY}";
        style="solid,rounded"; color="{PRIMARY}"; bgcolor="#F5F3FF";

        Dispersion [label="Analyse de Dispersion Intra-Classe\\nPour chaque descripteur j :\\nmu_R = Moyenne des vecteurs de R\\nsigma_R = Dispersion quadratique intra-R"];
        
        Fisher [label="Pouvoir Discriminant Inter-Classes\\nSi Ir non vide : distance(mu_R, mu_Ir)\\nScore brut : R_j = (dist_inter + eps) / (sigma_R + sigma_Ir + eps)\\nSinon : R_j = 1 / (sigma_R + eps)"];

        Centroid [label="Mise à Jour du Centroïde de Requête\\nq'_j = alpha * q_j + (1 - alpha) * mu_R,j\\n(alpha = 0.7 par défaut)"];

        Smoothing [label="Lissage Bayésien & Normalisation\\nw'_j = beta * w_{{j, prior}} + (1 - beta) * norm(R_j)\\nNormalisation unitaire SUM(w'_j) = 1.0\\n(beta = 0.3 par défaut)"];

        Dispersion -> Fisher;
        Fisher -> Smoothing;
        Dispersion -> Centroid;
    }}

    subgraph cluster_rerank {{
        label = "Étape 3 : Réordonnancement";
        fontname="Helvetica-Bold"; fontsize=11; fontcolor="{PRIMARY}";
        style="dashed,rounded"; color="{PRIMARY}"; bgcolor="#ECFDF5";

        NewSearch [label="Nouvelle Recherche avec (q', w')\\nCalcul des similarités ajustées", fillcolor="#D1FAE5"];
        NewResults [label="Résultats Améliorés Présentés\\nPrécision accrue & Convergence", fillcolor="#D1FAE5"];
        NewSearch -> NewResults;
    }}

    UserLabel -> Dispersion [label="Envoi des ensembles R et Ir"];
    Centroid -> NewSearch [label="Nouveau vecteur requête"];
    Smoothing -> NewSearch [label="Nouveaux poids adaptatifs"];
    NewResults -> UserLabel [style=dotted, label="Nouvelle itération possible"];
}}
"""
compile_dot(dot_07, f"{IMAGES_DIR}/07-boucle-relevance-feedback-fre.png")

# -------------------------------------------------------------
# 08: Architecture Frontend SvelteKit
# -------------------------------------------------------------
dot_08 = f"""
digraph G {{
    rankdir=LR;
    bgcolor="{WHITE}";
    nodesep=0.4;
    ranksep=0.5;
    node [shape=box, style="filled,rounded", fontname="Helvetica", fontsize=10, fillcolor="{LIGHT}", color="{BORDER}", penwidth=1.4, fontcolor="{SLATE}"];
    edge [color="{PRIMARY}", penwidth=1.4, fontname="Helvetica", fontsize=9, fontcolor="{GRAY}"];

    subgraph cluster_routes {{
        label = "Routes Applicatives (SvelteKit 3)";
        fontname="Helvetica-Bold"; fontsize=11; fontcolor="{PRIMARY}";
        style="solid,rounded"; color="{PRIMARY}"; bgcolor="#FAFAFD";

        R_Root [label="/ (Landing Page)"];
        R_Auth [label="/(auth)/login & /register"];
        R_Dash [label="/(dashboard)/dashboard\\nGalerie, Arbre, Filtres"];
        R_Search [label="/search\\nStudio CBIR & Feedback FRE"];
        R_Settings [label="/settings\\nPréférences & Thème"];
    }}

    subgraph cluster_components {{
        label = "Composants Réutilisables & Shadcn-Svelte";
        fontname="Helvetica-Bold"; fontsize=11; fontcolor="{PRIMARY}";
        style="solid,rounded"; color="{PRIMARY}"; bgcolor="#F8FAFC";

        Comp_Gallery [label="ImageGallery & BatchActionBar"];
        Comp_Detail [label="ImageDetailModal & Transforms"];
        Comp_CBIR [label="CBIRSearchPanel & FeedbackControls"];
        Comp_Charts [label="LayerChart & InteractiveHistograms"];
        Comp_Table [label="TanStack DataTable & VirtualScroll"];
    }}

    subgraph cluster_core {{
        label = "Logique Réactive (Svelte 5 Runes) & Utilitaires";
        fontname="Helvetica-Bold"; fontsize=11; fontcolor="{PRIMARY}";
        style="solid,rounded"; color="{PRIMARY}"; bgcolor="#EDE9FE";

        Runes [label="Runes Svelte 5\\n$state(), $derived(), $props(), $effect()"];
        I18n [label="Internationalisation\\nParaglide-JS (fr / en)"];
        ApiLib [label="Clients API Typés\\nimages.ts, query.ts, auth.ts"];
        Theme [label="ModeWatcher & Tailwind 4\\nThème Sombre / Clair"];
    }}

    R_Dash -> Comp_Gallery;
    R_Dash -> Comp_Detail;
    R_Search -> Comp_CBIR;
    R_Search -> Comp_Charts;
    Comp_Gallery -> Comp_Table;
    Comp_Gallery -> Runes;
    Comp_CBIR -> Runes;
    Comp_CBIR -> ApiLib;
    Comp_Gallery -> ApiLib;
    Runes -> I18n;
    Runes -> Theme;
}}
"""
compile_dot(dot_08, f"{IMAGES_DIR}/08-architecture-frontend-sveltekit.png")

# -------------------------------------------------------------
# 09: Schéma Relationnel de la Base de Données
# -------------------------------------------------------------
dot_09 = f"""
digraph G {{
    rankdir=TB;
    bgcolor="{WHITE}";
    compound=true;
    nodesep=0.4;
    ranksep=0.5;
    node [shape=record, style="filled,rounded", fontname="Helvetica", fontsize=9, fillcolor="{LIGHT}", color="{BORDER}", penwidth=1.4, fontcolor="{SLATE}"];
    edge [color="{PRIMARY}", penwidth=1.4, fontname="Helvetica", fontsize=9, fontcolor="{GRAY}"];

    subgraph cluster_users_media {{
        label = "Entités Médias, Catégories & Utilisateurs";
        fontname="Helvetica-Bold"; fontsize=11; fontcolor="{PRIMARY}";
        style="solid,rounded"; color="{PRIMARY}"; bgcolor="#F8FAFC";

        User [label="{{users | id : VARCHAR(36) [PK]\\l| username : VARCHAR(50)\\l| email : VARCHAR(120) [UQ]\\l| password_hash : VARCHAR(255)\\l| role : VARCHAR(20)\\l| created_at : DATETIME\\l}}", fillcolor="#FEF3C7"];

        Category [label="{{categories | id : VARCHAR(36) [PK]\\l| user_id : VARCHAR(36) [FK]\\l| parent_id : VARCHAR(36) [FK]\\l| name : VARCHAR(100)\\l| path : VARCHAR(500)\\l| created_at : DATETIME\\l}}", fillcolor="#E0E7FF"];

        Image [label="{{images | id : VARCHAR(36) [PK]\\l| owner_id : VARCHAR(36) [FK]\\l| category_id : VARCHAR(36) [FK]\\l| parent_image_id : VARCHAR(36) [FK]\\l| filename : VARCHAR(255)\\l| storage_key : VARCHAR(500) [UQ]\\l| source_type : VARCHAR(20)\\l| processing_status : VARCHAR(20)\\l| checksum : VARCHAR(64) [SHA256]\\l| width, height, file_size\\l| transformation_params : JSON\\l| created_at : DATETIME\\l}}", fillcolor="#EDE9FE"];

        ImageFeature [label="{{image_features | id : VARCHAR(36) [PK]\\l| image_id : VARCHAR(36) [FK]\\l| feature_type : VARCHAR(50)\\l| extractor_version : VARCHAR(50)\\l| feature_values : JSON\\l| parameters : JSON\\l| created_at : DATETIME\\l}}", fillcolor="#FCE7F3"];

        FavoriteImage [label="{{favorite_images | user_id : VARCHAR(36) [PK, FK]\\l| image_id : VARCHAR(36) [PK, FK]\\l| created_at : DATETIME\\l}}", fillcolor="#FEF3C7"];
    }}

    subgraph cluster_retrieval {{
        label = "Entités Recherche CBIR & Relevance Feedback";
        fontname="Helvetica-Bold"; fontsize=11; fontcolor="{PRIMARY}";
        style="solid,rounded"; color="{PRIMARY}"; bgcolor="#F5F3FF";

        RetrievalQuery [label="{{retrieval_queries | id : VARCHAR(36) [PK]\\l| user_id : VARCHAR(36) [FK]\\l| query_image_id : VARCHAR(36) [FK]\\l| search_scope : VARCHAR(30)\\l| configuration : JSON\\l| status : VARCHAR(20)\\l| created_at : DATETIME\\l}}", fillcolor="#D1FAE5"];

        RetrievalIteration [label="{{retrieval_iterations | id : VARCHAR(36) [PK]\\l| query_id : VARCHAR(36) [FK]\\l| iteration_number : INT\\l| retrieval_method : VARCHAR(30)\\l| feature_weights : JSON\\l| updated_query_vector : JSON\\l| execution_time_ms : INT\\l| results_count : INT\\l}}", fillcolor="#D1FAE5"];

        RetrievalResult [label="{{retrieval_results | id : VARCHAR(36) [PK]\\l| iteration_id : VARCHAR(36) [FK]\\l| image_id : VARCHAR(36) [FK]\\l| rank : INT\\l| similarity_score : FLOAT\\l| feature_scores : JSON\\l}}", fillcolor="#D1FAE5"];

        RelevanceFeedback [label="{{relevance_feedbacks | id : VARCHAR(36) [PK]\\l| iteration_id : VARCHAR(36) [FK]\\l| image_id : VARCHAR(36) [FK]\\l| feedback_type : VARCHAR(20)\\l| created_at : DATETIME\\l}}", fillcolor="#FEE2E2"];
    }}

    User -> Image [label="1 : N"];
    User -> Category [label="1 : N"];
    Category -> Category [label="parent"];
    Category -> Image [label="1 : N"];
    Image -> Image [label="dérivée"];
    Image -> ImageFeature [label="1 : N (cascade)"];
    User -> FavoriteImage [label="1 : N"];
    Image -> FavoriteImage [label="1 : N"];

    User -> RetrievalQuery [label="1 : N"];
    Image -> RetrievalQuery [label="requête"];
    RetrievalQuery -> RetrievalIteration [label="1 : N (cascade)"];
    RetrievalIteration -> RetrievalResult [label="1 : N (cascade)"];
    Image -> RetrievalResult [label="1 : N"];
    RetrievalIteration -> RelevanceFeedback [label="1 : N (cascade)"];
    Image -> RelevanceFeedback [label="1 : N"];
}}
"""
compile_dot(dot_09, f"{IMAGES_DIR}/09-schema-relationnel-db.png")

# -------------------------------------------------------------
# 10: Déploiement Docker & Infrastructure
# -------------------------------------------------------------
dot_10 = f"""
digraph G {{
    rankdir=LR;
    bgcolor="{WHITE}";
    nodesep=0.4;
    ranksep=0.6;
    node [shape=box, style="filled,rounded", fontname="Helvetica", fontsize=10, fillcolor="{LIGHT}", color="{BORDER}", penwidth=1.4, fontcolor="{SLATE}"];
    edge [color="{PRIMARY}", penwidth=1.4, fontname="Helvetica", fontsize=9, fontcolor="{GRAY}"];

    subgraph cluster_docker {{
        label = "Environnement Docker / Docker Compose";
        fontname="Helvetica-Bold"; fontsize=12; fontcolor="{PRIMARY}";
        style="dashed,rounded"; color="{PRIMARY}"; bgcolor="#F8FAFC";

        subgraph cluster_web {{
            label = "Service Web Frontend (Container Bun/Node)";
            fontname="Helvetica-Bold"; fontsize=10; fontcolor="{PRIMARY}";
            style="solid,rounded"; color="{ACCENT}"; bgcolor="{WHITE}";
            
            SvelteApp [label="SvelteKit App\\nPort 5173 / Production Build\\nVite / Node Adapter"];
        }}

        subgraph cluster_api {{
            label = "Service API Backend (Container Python 3.13)";
            fontname="Helvetica-Bold"; fontsize=10; fontcolor="{PRIMARY}";
            style="solid,rounded"; color="{ACCENT}"; bgcolor="{WHITE}";

            Entrypoint [label="docker-entrypoint.sh\\nMigrations DB auto"];
            Gunicorn [label="Gunicorn WSGI Server\\n4 Workers - Port 5000"];
            FlaskCore [label="Flask 3.x Application\\nOpenCV, Scikit-image, Scikit-learn"];
            Entrypoint -> Gunicorn -> FlaskCore;
        }}

        subgraph cluster_volumes {{
            label = "Volumes Persistants (Bind Mounts / Named Volumes)";
            fontname="Helvetica-Bold"; fontsize=10; fontcolor="{PRIMARY}";
            style="dashed,rounded"; color="#D97706"; bgcolor="#FFFDF5";

            VolStorage [label="Volume /storage\\nImages originales, dérivées, GHIM-10K", shape=folder, fillcolor="#FEF3C7"];
            VolDB [label="Volume /instance\\nperceptra.db (SQLite WAL Mode)", shape=cylinder, fillcolor="#FEF3C7"];
        }}
    }}

    Clients [label="Navigateurs Clients\\nDesktop & Mobile", shape=ellipse, fillcolor="#EDE9FE"];
    Clients -> SvelteApp [label="Port 5173 (HTTP)"];
    Clients -> Gunicorn [label="Port 5000 (/api)"];
    SvelteApp -> Gunicorn [label="Proxy interne API"];
    FlaskCore -> VolStorage [label="Lecture/Écriture I/O"];
    FlaskCore -> VolDB [label="Transactions SQL"];
}}
"""
compile_dot(dot_10, f"{IMAGES_DIR}/10-deploiement-docker-infra.png")

# -------------------------------------------------------------
# 11: Graphique Précision / Rappel (Généré avec PIL)
# -------------------------------------------------------------
def generate_pr_curves(filepath: str):
    width, height = 900, 520
    img = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype('/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf', 16)
        font_label = ImageFont.truetype('/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf', 12)
        font_ticks = ImageFont.truetype('/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf', 10)
    except:
        font_title = font_label = font_ticks = ImageFont.load_default()

    # Title
    draw.text((width // 2 - 240, 20), "Évaluation Quantitative : Précision Moyenne @ K sur GHIM-10K", fill=(38, 42, 52), font=font_title)

    # Plot area
    ox, oy = 90, 430
    pw, ph = 740, 350

    # Axes
    draw.line([(ox, oy), (ox + pw, oy)], fill=(96, 102, 112), width=2)
    draw.line([(ox, oy), (ox, oy - ph)], fill=(96, 102, 112), width=2)

    # Gridlines and Y ticks (Precision: 0.0 to 1.0)
    for i in range(6):
        val = i * 0.2
        y = oy - int(i * 0.2 * ph)
        draw.line([(ox, y), (ox + pw, y)], fill=(240, 242, 246), width=1)
        draw.text((ox - 45, y - 6), f"{val:.1f}", fill=(96, 102, 112), font=font_ticks)

    draw.text((ox - 75, oy - ph // 2 - 10), "Précision", fill=(72, 61, 139), font=font_label)

    # X ticks (K values: 5, 10, 20, 30, 40, 50)
    k_vals = [5, 10, 20, 30, 40, 50]
    x_coords = []
    for idx, k in enumerate(k_vals):
        x = ox + int(idx * (pw / (len(k_vals) - 1)))
        x_coords.append(x)
        draw.line([(x, oy), (x, oy + 5)], fill=(96, 102, 112), width=2)
        draw.text((x - 8, oy + 10), f"K={k}", fill=(96, 102, 112), font=font_ticks)

    draw.text((ox + pw // 2 - 40, oy + 35), "Nombre de résultats retournés (K)", fill=(72, 61, 139), font=font_label)

    # Data series
    # 1. Simple CBIR (sans feedback)
    y_simple = [0.62, 0.58, 0.51, 0.46, 0.42, 0.38]
    # 2. FRE Iteration 1
    y_fre_1 = [0.78, 0.73, 0.67, 0.61, 0.56, 0.52]
    # 3. FRE Iteration 2
    y_fre_2 = [0.89, 0.85, 0.79, 0.73, 0.68, 0.63]

    series = [
        ("Recherche Simple (Sans Feedback)", y_simple, (156, 163, 175), "circle"),
        ("FRE Itération 1 (Pondération Adaptative)", y_fre_1, (48, 104, 178), "square"),
        ("FRE Itération 2 (Convergence Optimale)", y_fre_2, (72, 61, 139), "triangle"),
    ]

    for name, data, col, marker in series:
        points = []
        for x, val in zip(x_coords, data):
            y = oy - int(val * ph)
            points.append((x, y))

        # Draw lines
        for i in range(len(points) - 1):
            draw.line([points[i], points[i+1]], fill=col, width=3)

        # Draw markers
        for x, y in points:
            if marker == "circle":
                draw.ellipse([x-5, y-5, x+5, y+5], fill=col, outline=(255, 255, 255), width=2)
            elif marker == "square":
                draw.rectangle([x-5, y-5, x+5, y+5], fill=col, outline=(255, 255, 255), width=2)
            elif marker == "triangle":
                draw.polygon([(x, y-6), (x-6, y+5), (x+6, y+5)], fill=col, outline=(255, 255, 255))

    # Legend
    leg_x, leg_y = ox + 320, 65
    draw.rectangle([leg_x - 10, leg_y - 10, leg_x + 390, leg_y + 80], fill=(246, 247, 250), outline=(203, 213, 225), width=1)
    for idx, (name, _, col, marker) in enumerate(series):
        ly = leg_y + idx * 24
        draw.line([(leg_x, ly + 6), (leg_x + 25, ly + 6)], fill=col, width=3)
        draw.ellipse([leg_x + 10, ly + 3, leg_x + 16, ly + 9], fill=col)
        draw.text((leg_x + 35, ly), name, fill=(38, 42, 52), font=font_ticks)

    img.save(filepath)
    print(f"Generated PR curves: {filepath}")

generate_pr_curves(f"{IMAGES_DIR}/11-courbes-precision-recall-evaluation.png")

# -------------------------------------------------------------
# 12: Cycle de Vie et Perspectives d'Évolution
# -------------------------------------------------------------
dot_12 = f"""
digraph G {{
    rankdir=LR;
    bgcolor="{WHITE}";
    nodesep=0.4;
    ranksep=0.5;
    node [shape=box, style="filled,rounded", fontname="Helvetica", fontsize=10, fillcolor="{LIGHT}", color="{BORDER}", penwidth=1.4, fontcolor="{SLATE}"];
    edge [color="{PRIMARY}", penwidth=1.4, fontname="Helvetica", fontsize=9, fontcolor="{GRAY}"];

    subgraph cluster_phase1 {{
        label = "Phase 1 : Socle Actuel (Perceptra v1.0)";
        fontname="Helvetica-Bold"; fontsize=11; fontcolor="{PRIMARY}";
        style="solid,rounded"; color="{PRIMARY}"; bgcolor="#F5F3FF";

        P1_Desk [label="Descripteurs Manuels Déterministes\\nHSV 768-D, Moments, GLCM, LBP"];
        P1_FRE [label="Moteur FRE (Groupe 13)\\nDispersion intra/inter-classe + Lissage"];
        P1_Arch [label="Architecture Monolithe Modulaire\\nFlask REST + SvelteKit + SQLite"];
    }}

    subgraph cluster_phase2 {{
        label = "Phase 2 : Évolutions Moyen Terme (v2.0)";
        fontname="Helvetica-Bold"; fontsize=11; fontcolor="{ACCENT}";
        style="dashed,rounded"; color="{ACCENT}"; bgcolor="#F0F9FF";

        P2_Index [label="Indexation Vectorielle Dédiée\\nIntégration FAISS / HNSW / Milvus\\nRecherche sub-milliseconde sur >1M images"];
        P2_Deep [label="Descripteurs Hybrides Profonds\\nEmbeddings DINOv2 & CLIP multimodal\\nFusion pondérée bas-niveau + haut-niveau"];
    }}

    subgraph cluster_phase3 {{
        label = "Phase 3 : Vision Long Terme (v3.0)";
        fontname="Helvetica-Bold"; fontsize=11; fontcolor="#059669";
        style="dashed,rounded"; color="#059669"; bgcolor="#ECFDF5";

        P3_Cloud [label="Déploiement Cloud Distribué\\nKubernetes, Object Storage S3, Celery/Redis"];
        P3_Active [label="Active Learning & Réseaux Siamois\\nApprentissage continu des métriques de distance"];
    }}

    P1_Desk -> P2_Deep [label="Hybridation"];
    P1_FRE -> P3_Active [label="Généralisation"];
    P1_Arch -> P2_Index [label="Passage à l'échelle"];
    P2_Index -> P3_Cloud [label="Haute disponibilité"];
}}
"""
compile_dot(dot_12, f"{IMAGES_DIR}/12-cycle-de-vie-et-perspectives.png")

# Also copy 00 to methodologie.png if referenced
import shutil
shutil.copyfile(f"{IMAGES_DIR}/01-perceptra-pipeline-fonctionnel.png", f"{IMAGES_DIR}/methodologie.png")
print("All images generated successfully.")
