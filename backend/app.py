from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime
from google.cloud import vision
import io
from agent import Agent

# Set Google Cloud credentials explicitly
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.join(os.path.dirname(__file__), 'service-account-key.json')
print(f"Google Cloud credentials set to: {os.environ['GOOGLE_APPLICATION_CREDENTIALS']}")
print(f"Credentials file exists: {os.path.exists(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])}")

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'zip', 'rar'}

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def cleanup_old_images(max_images=5):
    """Keep only the most recent images, delete the oldest ones"""
    try:
        # Get all image files in upload directory
        image_files = []
        for filename in os.listdir(UPLOAD_FOLDER):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                # Get file modification time
                mtime = os.path.getmtime(file_path)
                image_files.append((filename, mtime))
        
        # Sort by modification time (newest first)
        image_files.sort(key=lambda x: x[1], reverse=True)
        
        # Delete oldest files if we have more than max_images
        if len(image_files) > max_images:
            files_to_delete = image_files[max_images:]
            for filename, _ in files_to_delete:
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                try:
                    os.remove(file_path)
                    print(f"🗑️ Cleaned up old image: {filename}")
                except Exception as e:
                    print(f"⚠️ Could not delete old image {filename}: {e}")
                    
        print(f"📊 Image cleanup complete. Keeping {min(len(image_files), max_images)} images.")
        
    except Exception as e:
        print(f"⚠️ Error during image cleanup: {e}")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def analyze_image_with_vision(image_path):
    """Analyze image using Google Vision API to detect artwork"""
    try:
        print(f"Starting analysis for: {image_path}")
        
        # Initialize the Vision API client
        client = vision.ImageAnnotatorClient()
        print("Vision client created successfully")
        
        # Read the image file
        with io.open(image_path, 'rb') as image_file:
            content = image_file.read()
        
        print(f"Image file read successfully, size: {len(content)} bytes")
        
        image = vision.Image(content=content)
        
        # Perform label detection
        print("Performing label detection...")
        response = client.label_detection(image=image)
        labels = response.label_annotations
        print(f"Found {len(labels)} labels")
        
        # Perform web detection for famous artwork
        print("Performing web detection...")
        web_response = client.web_detection(image=image)
        web_entities = web_response.web_detection.web_entities if web_response.web_detection else []
        print(f"Found {len(web_entities)} web entities")
        
        # Look for art-related labels
        art_labels = []
        artwork_name = None
        artist_name = None
        confidence = 0
        
        # Check labels for art-related terms
        for label in labels:
            label_text = label.description.lower()
            print(f"Checking label: {label.description} (confidence: {label.score})")
            if any(term in label_text for term in ['art', 'painting', 'drawing', 'sculpture', 'artwork', 'portrait', 'landscape', 'still life', 'masterpiece']):
                art_labels.append({
                    'description': label.description,
                    'confidence': label.score
                })
                print(f"Found art-related label: {label.description}")
        
        # PRIORITIZE WEB ENTITIES - they're much more accurate for specific artwork
        print("Checking web entities for artwork...")
        
        # Define famous artworks and artists for better classification
        famous_artworks = [
            'starry night', 'mona lisa', 'the scream', 'guernica', 'the persistence of memory',
            'water lilies', 'the last supper', 'the birth of venus', 'american gothic', 'the great wave',
            'david', 'the creation of adam', 'the sistine chapel', 'the school of athens',
            'girl with a pearl earring', 'the night watch', 'the kiss', 'the thinker',
            'les demoiselles d\'avignon', 'the blue rider', 'composition vii', 'no. 5',
            'campbell\'s soup cans', 'marilyn diptych', 'the persistence of memory',
            'the great wave off kanagawa', 'the birth of venus', 'girl before a mirror',
            'the old guitarist', 'les demoiselles d\'avignon', 'guernica', 'the weeping woman',
            'three musicians', 'the blue period', 'rose period', 'cubism'
        ]
        
        famous_artists = [
            'michelangelo', 'leonardo da vinci', 'vincent van gogh', 'pablo picasso',
            'claude monet', 'edvard munch', 'salvador dali', 'rembrandt', 'andy warhol',
            'jackson pollock', 'wassily kandinsky', 'henri matisse', 'auguste rodin',
            'gustav klimt', 'paul gauguin', 'paul cezanne', 'edgar degas', 'mary cassatt',
            'frida kahlo', 'georgia o\'keeffe', 'mark rothko', 'willem de kooning',
            'leonardo', 'picasso', 'van gogh', 'monet', 'dali', 'warhol', 'pollock',
            'kandinsky', 'matisse', 'rodin', 'klimt', 'gauguin', 'cezanne', 'degas'
        ]
        
        # Separate entities into artwork and artist candidates
        artwork_candidates = []
        artist_candidates = []
        
        for entity in web_entities:
            print(f"Web entity: {entity.description} (score: {entity.score})")
            entity_desc = entity.description.lower()
            
            if entity.score > 0.2:  # Low threshold to catch everything
                # Check if it's a famous artwork
                is_famous_artwork = any(artwork in entity_desc for artwork in famous_artworks)
                # Check if it's a famous artist
                is_famous_artist = any(artist in entity_desc for artist in famous_artists)
                
                if is_famous_artwork and not is_famous_artist:
                    artwork_candidates.append({
                        'name': entity.description,
                        'score': entity.score,
                        'type': 'famous_artwork'
                    })
                    print(f"Found famous artwork: {entity.description}")
                elif is_famous_artist and not is_famous_artwork:
                    artist_candidates.append({
                        'name': entity.description,
                        'score': entity.score,
                        'type': 'famous_artist'
                    })
                    print(f"Found famous artist: {entity.description}")
                else:
                    # Check for generic terms that we want to avoid
                    generic_terms = ['painting', 'sculpture', 'artwork', 'masterpiece', 'statue', 'bust', 'portrait', 'landscape', 'still life', 'art', 'image', 'picture', 'photo', 'photograph', 'drawing', 'sketch', 'canvas', 'oil painting', 'watercolor', 'acrylic', 'mixed media', 'collage', 'print', 'etching', 'lithograph', 'fresco', 'mural', 'relief', 'installation', 'performance art', 'digital art', 'conceptual art', 'abstract art', 'figurative art', 'contemporary art', 'modern art', 'classical art', 'fine art', 'visual art', 'graphic art', 'decorative art', 'applied art', 'folk art', 'naive art', 'primitive art', 'cave painting', 'rock art', 'street art', 'graffiti', 'mosaic', 'tapestry', 'ceramic', 'pottery', 'glass art', 'metalwork', 'wood carving', 'stone carving', 'bronze', 'marble', 'plaster', 'clay', 'textile', 'fiber art', 'jewelry', 'furniture', 'architecture', 'design', 'illustration', 'poster', 'book cover', 'album cover', 'logo', 'symbol', 'icon', 'emblem', 'badge', 'medal', 'coin', 'stamp', 'postcard', 'calendar', 'magazine', 'newspaper', 'advertisement', 'billboard', 'sign', 'banner', 'flag', 'banner', 'pennant', 'streamer', 'decoration', 'ornament', 'accessory', 'gift', 'souvenir', 'keepsake', 'memento', 'relic', 'artifact', 'antique', 'vintage', 'collectible', 'curio', 'trinket', 'bauble', 'knickknack', 'bric-a-brac', 'gewgaw', 'gimcrack', 'novelty', 'toy', 'game', 'puzzle', 'model', 'miniature', 'replica', 'copy', 'reproduction', 'facsimile', 'duplicate', 'clone', 'imitation', 'fake', 'forgery', 'counterfeit', 'knockoff', 'bootleg', 'pirate', 'unauthorized', 'illegal', 'stolen', 'looted', 'smuggled', 'contraband', 'black market', 'underground', 'secret', 'hidden', 'concealed', 'camouflaged', 'disguised', 'masked', 'veiled', 'covered', 'wrapped', 'packaged', 'boxed', 'crated', 'shipped', 'delivered', 'transported', 'moved', 'relocated', 'transferred', 'sold', 'bought', 'purchased', 'acquired', 'obtained', 'gained', 'earned', 'won', 'lost', 'stolen', 'taken', 'removed', 'destroyed', 'damaged', 'broken', 'fixed', 'repaired', 'restored', 'conserved', 'preserved', 'maintained', 'cleaned', 'polished', 'refinished', 'refurbished', 'renovated', 'updated', 'modernized', 'improved', 'enhanced', 'upgraded', 'modified', 'altered', 'changed', 'transformed', 'converted', 'adapted', 'adjusted', 'customized', 'personalized', 'tailored', 'fitted', 'sized', 'scaled', 'proportioned', 'balanced', 'harmonized', 'coordinated', 'matched', 'paired', 'grouped', 'categorized', 'classified', 'sorted', 'organized', 'arranged', 'displayed', 'exhibited', 'shown', 'presented', 'demonstrated', 'explained', 'described', 'documented', 'recorded', 'catalogued', 'indexed', 'referenced', 'cited', 'quoted', 'mentioned', 'noted', 'observed', 'noticed', 'spotted', 'seen', 'viewed', 'looked', 'watched', 'studied', 'examined', 'analyzed', 'evaluated', 'assessed', 'judged', 'critiqued', 'reviewed', 'rated', 'ranked', 'scored', 'graded', 'marked', 'labeled', 'tagged', 'named', 'titled', 'captioned', 'subtitled', 'legend', 'inscription', 'text', 'writing', 'script', 'font', 'typeface', 'typography', 'calligraphy', 'handwriting', 'signature', 'autograph', 'monogram', 'initial', 'letter', 'word', 'phrase', 'sentence', 'paragraph', 'passage', 'excerpt', 'quote', 'citation', 'reference', 'footnote', 'endnote', 'bibliography', 'source', 'origin', 'provenance', 'history', 'background', 'context', 'setting', 'environment', 'atmosphere', 'mood', 'feeling', 'emotion', 'sentiment', 'attitude', 'opinion', 'viewpoint', 'perspective', 'angle', 'approach', 'method', 'technique', 'style', 'manner', 'way', 'fashion', 'trend', 'movement', 'school', 'tradition', 'convention', 'standard', 'norm', 'rule', 'principle', 'guideline', 'criterion', 'measure', 'yardstick', 'benchmark', 'reference point', 'baseline', 'starting point', 'foundation', 'basis', 'ground', 'reason', 'cause', 'purpose', 'goal', 'objective', 'aim', 'target', 'destination', 'end', 'result', 'outcome', 'consequence', 'effect', 'impact', 'influence', 'significance', 'importance', 'value', 'worth', 'merit', 'quality', 'excellence', 'superiority', 'greatness', 'brilliance', 'genius', 'talent', 'skill', 'ability', 'capability', 'competence', 'proficiency', 'expertise', 'mastery', 'virtuosity', 'artistry', 'craftsmanship', 'workmanship', 'technique', 'method', 'approach', 'style', 'manner', 'way', 'fashion', 'mode', 'form', 'format', 'structure', 'organization', 'arrangement', 'composition', 'design', 'layout', 'pattern', 'motif', 'theme', 'subject', 'topic', 'content', 'material', 'medium', 'substance', 'matter', 'stuff', 'thing', 'object', 'item', 'piece', 'work', 'creation', 'production', 'output', 'result', 'product', 'artifact', 'specimen', 'sample', 'example', 'instance', 'case', 'occurrence', 'event', 'happening', 'incident', 'episode', 'scene', 'moment', 'instant', 'second', 'minute', 'hour', 'day', 'week', 'month', 'year', 'decade', 'century', 'millennium', 'era', 'period', 'age', 'time', 'date', 'chronology', 'timeline', 'history', 'past', 'present', 'future', 'now', 'then', 'when', 'where', 'why', 'how', 'what', 'who', 'which', 'whose', 'whom', 'that', 'this', 'these', 'those', 'here', 'there', 'everywhere', 'nowhere', 'somewhere', 'anywhere', 'always', 'never', 'sometimes', 'often', 'rarely', 'usually', 'normally', 'typically', 'generally', 'commonly', 'frequently', 'occasionally', 'seldom', 'hardly', 'barely', 'scarcely', 'almost', 'nearly', 'quite', 'very', 'extremely', 'highly', 'greatly', 'significantly', 'substantially', 'considerably', 'remarkably', 'notably', 'particularly', 'especially', 'specifically', 'particularly', 'especially', 'specifically', 'particularly', 'especially', 'specifically']
                    artist_terms = ['artist', 'painter', 'sculptor', 'creator', 'maker', 'designer', 'illustrator', 'draftsman', 'cartoonist', 'animator', 'photographer', 'filmmaker', 'director', 'producer', 'writer', 'author', 'poet', 'novelist', 'playwright', 'screenwriter', 'composer', 'musician', 'singer', 'performer', 'actor', 'actress', 'dancer', 'choreographer', 'architect', 'engineer', 'scientist', 'inventor', 'discoverer', 'explorer', 'adventurer', 'traveler', 'tourist', 'visitor', 'guest', 'host', 'owner', 'collector', 'curator', 'critic', 'reviewer', 'journalist', 'reporter', 'editor', 'publisher', 'agent', 'manager', 'dealer', 'gallery', 'museum', 'exhibition', 'show', 'display', 'collection', 'archive', 'library', 'database', 'catalog', 'inventory', 'stock', 'supply', 'store', 'shop', 'market', 'fair', 'auction', 'sale', 'purchase', 'buy', 'sell', 'trade', 'exchange', 'barter', 'negotiate', 'deal', 'contract', 'agreement', 'arrangement', 'plan', 'scheme', 'project', 'program', 'initiative', 'campaign', 'movement', 'organization', 'institution', 'foundation', 'trust', 'fund', 'endowment', 'grant', 'scholarship', 'award', 'prize', 'honor', 'recognition', 'accolade', 'commendation', 'praise', 'compliment', 'tribute', 'memorial', 'monument', 'statue', 'sculpture', 'bust', 'relief', 'plaque', 'inscription', 'epitaph', 'tombstone', 'gravestone', 'headstone', 'marker', 'sign', 'symbol', 'emblem', 'badge', 'medal', 'ribbon', 'certificate', 'diploma', 'degree', 'title', 'rank', 'position', 'status', 'standing', 'reputation', 'fame', 'celebrity', 'star', 'icon', 'legend', 'myth', 'hero', 'heroine', 'champion', 'winner', 'victor', 'conqueror', 'leader', 'ruler', 'king', 'queen', 'emperor', 'empress', 'president', 'prime minister', 'governor', 'mayor', 'chief', 'boss', 'manager', 'supervisor', 'director', 'executive', 'administrator', 'official', 'representative', 'ambassador', 'delegate', 'spokesperson', 'spokesman', 'spokeswoman', 'advocate', 'supporter', 'fan', 'follower', 'admirer', 'devotee', 'enthusiast', 'lover', 'friend', 'companion', 'partner', 'associate', 'colleague', 'teammate', 'ally', 'supporter', 'helper', 'assistant', 'aide', 'secretary', 'clerk', 'employee', 'worker', 'staff', 'personnel', 'crew', 'team', 'group', 'organization', 'company', 'corporation', 'business', 'enterprise', 'firm', 'agency', 'bureau', 'office', 'department', 'division', 'section', 'unit', 'branch', 'subsidiary', 'affiliate', 'partner', 'associate', 'member', 'participant', 'contributor', 'donor', 'sponsor', 'patron', 'benefactor', 'supporter', 'backer', 'investor', 'shareholder', 'stakeholder', 'owner', 'proprietor', 'landlord', 'tenant', 'resident', 'inhabitant', 'citizen', 'national', 'native', 'local', 'foreigner', 'immigrant', 'emigrant', 'refugee', 'exile', 'outcast', 'pariah', 'reject', 'failure', 'loser', 'victim', 'casualty', 'survivor', 'witness', 'observer', 'spectator', 'audience', 'crowd', 'mob', 'group', 'gang', 'band', 'crew', 'team', 'squad', 'unit', 'force', 'army', 'navy', 'air force', 'marines', 'coast guard', 'police', 'sheriff', 'marshal', 'detective', 'inspector', 'agent', 'officer', 'soldier', 'sailor', 'pilot', 'captain', 'commander', 'general', 'admiral', 'colonel', 'major', 'captain', 'lieutenant', 'sergeant', 'corporal', 'private', 'cadet', 'recruit', 'veteran', 'retiree', 'pensioner', 'senior', 'elder', 'adult', 'teenager', 'youth', 'child', 'baby', 'infant', 'toddler', 'preschooler', 'kindergartener', 'student', 'pupil', 'scholar', 'academic', 'professor', 'teacher', 'instructor', 'tutor', 'mentor', 'coach', 'trainer', 'guide', 'leader', 'director', 'manager', 'supervisor', 'boss', 'chief', 'head', 'president', 'chairman', 'chairwoman', 'chairperson', 'speaker', 'moderator', 'facilitator', 'mediator', 'arbitrator', 'judge', 'justice', 'magistrate', 'commissioner', 'administrator', 'executive', 'official', 'representative', 'delegate', 'ambassador', 'envoy', 'messenger', 'courier', 'delivery', 'mail', 'post', 'package', 'parcel', 'envelope', 'letter', 'note', 'message', 'communication', 'correspondence', 'email', 'text', 'call', 'phone', 'telephone', 'mobile', 'cell', 'smartphone', 'tablet', 'computer', 'laptop', 'desktop', 'server', 'network', 'internet', 'web', 'website', 'page', 'site', 'link', 'url', 'address', 'location', 'place', 'spot', 'point', 'position', 'coordinate', 'latitude', 'longitude', 'altitude', 'elevation', 'depth', 'height', 'width', 'length', 'size', 'dimension', 'measurement', 'scale', 'proportion', 'ratio', 'percentage', 'fraction', 'decimal', 'number', 'digit', 'figure', 'statistic', 'data', 'information', 'fact', 'detail', 'particular', 'specific', 'general', 'universal', 'global', 'worldwide', 'international', 'national', 'regional', 'local', 'municipal', 'city', 'town', 'village', 'hamlet', 'settlement', 'community', 'neighborhood', 'district', 'ward', 'precinct', 'zone', 'area', 'region', 'territory', 'country', 'nation', 'state', 'province', 'county', 'parish', 'borough', 'canton', 'department', 'prefecture', 'governorate', 'emirate', 'sultanate', 'kingdom', 'empire', 'republic', 'democracy', 'monarchy', 'dictatorship', 'autocracy', 'oligarchy', 'aristocracy', 'plutocracy', 'theocracy', 'anarchy', 'chaos', 'order', 'law', 'rule', 'regulation', 'policy', 'procedure', 'protocol', 'standard', 'norm', 'convention', 'tradition', 'custom', 'habit', 'practice', 'routine', 'ritual', 'ceremony', 'celebration', 'festival', 'holiday', 'vacation', 'break', 'rest', 'relaxation', 'leisure', 'entertainment', 'amusement', 'fun', 'enjoyment', 'pleasure', 'happiness', 'joy', 'delight', 'satisfaction', 'contentment', 'fulfillment', 'achievement', 'success', 'accomplishment', 'victory', 'triumph', 'conquest', 'domination', 'control', 'power', 'authority', 'influence', 'impact', 'effect', 'result', 'outcome', 'consequence', 'implication', 'significance', 'importance', 'value', 'worth', 'merit', 'quality', 'excellence', 'superiority', 'greatness', 'brilliance', 'genius', 'talent', 'skill', 'ability', 'capability', 'competence', 'proficiency', 'expertise', 'mastery', 'virtuosity', 'artistry', 'craftsmanship', 'workmanship', 'technique', 'method', 'approach', 'style', 'manner', 'way', 'fashion', 'mode', 'form', 'format', 'structure', 'organization', 'arrangement', 'composition', 'design', 'layout', 'pattern', 'motif', 'theme', 'subject', 'topic', 'content', 'material', 'medium', 'substance', 'matter', 'stuff', 'thing', 'object', 'item', 'piece', 'work', 'creation', 'production', 'output', 'result', 'product', 'artifact', 'specimen', 'sample', 'example', 'instance', 'case', 'occurrence', 'event', 'happening', 'incident', 'episode', 'scene', 'moment', 'instant', 'second', 'minute', 'hour', 'day', 'week', 'month', 'year', 'decade', 'century', 'millennium', 'era', 'period', 'age', 'time', 'date', 'chronology', 'timeline', 'history', 'past', 'present', 'future', 'now', 'then', 'when', 'where', 'why', 'how', 'what', 'who', 'which', 'whose', 'whom', 'that', 'this', 'these', 'those', 'here', 'there', 'everywhere', 'nowhere', 'somewhere', 'anywhere', 'always', 'never', 'sometimes', 'often', 'rarely', 'usually', 'normally', 'typically', 'generally', 'commonly', 'frequently', 'occasionally', 'seldom', 'hardly', 'barely', 'scarcely', 'almost', 'nearly', 'quite', 'very', 'extremely', 'highly', 'greatly', 'significantly', 'substantially', 'considerably', 'remarkably', 'notably', 'particularly', 'especially', 'specifically']
                    
                    is_generic = any(term in entity_desc for term in generic_terms)
                    is_artist = any(term in entity_desc for term in artist_terms)
                    
                    # Only add to candidates if it's NOT generic and NOT clearly an artist
                    if not is_generic and not is_artist and entity.score > 0.4:
                        artwork_candidates.append({
                            'name': entity.description,
                            'score': entity.score,
                            'type': 'unknown'
                        })
                        print(f"Found potential artwork: {entity.description}")
                    elif is_artist and not is_generic and entity.score > 0.6:
                        artist_candidates.append({
                            'name': entity.description,
                            'score': entity.score,
                            'type': 'generic_artist'
                        })
                        print(f"Found generic artist: {entity.description}")
        
        # Select the best artwork (highest confidence among artwork candidates)
        if artwork_candidates:
            # Sort by confidence score only - highest confidence wins
            artwork_candidates.sort(key=lambda x: x['score'], reverse=True)
            best_artwork = artwork_candidates[0]
            artwork_name = best_artwork['name']
            confidence = best_artwork['score']
            print(f"Selected artwork: {artwork_name} (type: {best_artwork['type']}, score: {confidence})")
        
        # Select the best artist
        if artist_candidates:
            artist_candidates.sort(key=lambda x: x['score'], reverse=True)
            artist_name = artist_candidates[0]['name']
            print(f"Selected artist: {artist_name}")
        
        # If no specific artwork title found, show "Artwork could not be found"
        if not artwork_name:
            artwork_name = "Artwork could not be found"
            confidence = 0
            print("No specific artwork title found - showing 'Artwork could not be found'")
        
        # Extract artist name from artwork name (common patterns)
        if artwork_name and not artist_name:
            artwork_lower = artwork_name.lower()
            print(f"Trying to extract artist from: {artwork_name}")
            
            # Pattern 1: "Artwork Name by Artist Name"
            if ' by ' in artwork_lower:
                parts = artwork_name.split(' by ', 1)
                if len(parts) == 2:
                    artwork_name = parts[0].strip()
                    artist_name = parts[1].strip()
                    print(f"Extracted artist from 'by': {artist_name}")
            
            # Pattern 2: "Artist Name - Artwork Name"
            elif ' - ' in artwork_lower:
                parts = artwork_name.split(' - ', 1)
                if len(parts) == 2:
                    artist_name = parts[0].strip()
                    artwork_name = parts[1].strip()
                    print(f"Extracted artist from '-': {artist_name}")
            
            # Pattern 3: Look for common artist names in the artwork name
            elif any(name in artwork_lower for name in ['van gogh', 'picasso', 'monet', 'da vinci', 'michelangelo', 'rembrandt', 'warhol', 'dali', 'kandinsky', 'pollock']):
                for name in ['van gogh', 'picasso', 'monet', 'da vinci', 'michelangelo', 'rembrandt', 'warhol', 'dali', 'kandinsky', 'pollock']:
                    if name in artwork_lower:
                        artist_name = name.title()
                        print(f"Found artist name in artwork: {artist_name}")
                        break
        
        # If still no artist found, look in web entities again with lower threshold
        if not artist_name:
            for entity in web_entities:
                entity_desc = entity.description.lower()
                if entity.score > 0.4:  # Lower threshold
                    if any(term in entity_desc for term in ['artist', 'painter', 'sculptor', 'creator']):
                        artist_name = entity.description
                        print(f"Found artist in web entities: {artist_name}")
                        break
        
        # Clean up the names
        if artwork_name:
            artwork_name = artwork_name.strip()
        if artist_name:
            artist_name = artist_name.strip()
        
        # Store the detected artwork name in a separate variable (not displayed)
        detected_artwork_name = artwork_name or 'Unknown Artwork'
        
        # Initialize the Agent with the detected artwork name for theme analysis
        try:
            artwork_agent = Agent("artwork", detected_artwork_name)
            artwork_agent.add_artwork_to_prompt()
            print(f"Agent initialized with artwork: {detected_artwork_name}")
        except Exception as e:
            print(f"Failed to initialize Agent: {str(e)}")
            artwork_agent = None
        
        result = {
            'artwork_name': artwork_name or 'Unknown Artwork',
            'artist_name': artist_name or 'Unknown Artist',
            'confidence': confidence,
            'art_labels': art_labels,
            'web_entities': [{'description': e.description, 'score': e.score} for e in web_entities[:5]],
            'agent_initialized': artwork_agent is not None
        }
        
        # Log the detected artwork name for debugging/logging purposes
        print(f"Detected artwork name (stored in variable): {detected_artwork_name}")
        
        print(f"Analysis complete: {result}")
        return result
        
    except Exception as e:
        print(f"Error in analyze_image_with_vision: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return {
            'artwork_name': 'Analysis Failed',
            'artist_name': 'Unknown Artist',
            'confidence': 0,
            'error': str(e),
            'art_labels': [],
            'web_entities': []
        }

@app.route('/')
def index():
    """Serve the main upload page"""
    return send_from_directory('../frontend', 'index.html')

@app.route('/styles.css')
def styles():
    """Serve CSS file"""
    return send_from_directory('../frontend', 'styles.css')

@app.route('/script.js')
def script():
    """Serve JavaScript file"""
    return send_from_directory('../frontend', 'script.js')

@app.route('/upload', methods=['POST'])
def upload_files():
    """Handle file uploads"""
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        
        if not files or all(file.filename == '' for file in files):
            return jsonify({'error': 'No files selected'}), 400
        
        uploaded_files = []
        failed_uploads = []
        
        for file in files:
            if file and allowed_file(file.filename):
                # Generate unique filename to prevent conflicts
                original_filename = secure_filename(file.filename)
                file_extension = original_filename.rsplit('.', 1)[1].lower()
                unique_filename = f"{uuid.uuid4()}.{file_extension}"
                
                # Save file
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                
                # Store file info
                file_info = {
                    'original_name': original_filename,
                    'saved_name': unique_filename,
                    'size': os.path.getsize(file_path),
                    'upload_time': datetime.now().isoformat()
                }
                
                # Analyze image for artwork if it's an image file
                print(f"File extension: {file_extension}")
                print(f"Checking if {file_extension} is in {['jpg', 'jpeg', 'png', 'gif']}")
                if file_extension in ['jpg', 'jpeg', 'png', 'gif']:
                    print(f"✅ Image file detected! Analyzing: {original_filename}")
                    print(f"File path: {file_path}")
                    try:
                        analysis_result = analyze_image_with_vision(file_path)
                        print(f"Analysis result: {analysis_result}")
                        file_info['artwork_analysis'] = analysis_result
                        
                        # Keep the image for display - cleanup will handle old images
                        print(f"📸 Keeping image for display: {file_path}")
                            
                    except Exception as e:
                        print(f"❌ Error analyzing image: {e}")
                        import traceback
                        traceback.print_exc()
                        file_info['artwork_analysis'] = {
                            'artwork_name': 'Analysis Error',
                            'confidence': 0,
                            'error': str(e)
                        }
                        
                        # Keep the image even if analysis failed
                        print(f"📸 Keeping image despite analysis error: {file_path}")
                else:
                    print(f"❌ Not an image file: {file_extension}")
                    # Delete non-image files immediately
                    try:
                        os.remove(file_path)
                        print(f"🗑️ Deleted non-image file: {file_path}")
                    except Exception as delete_error:
                        print(f"⚠️ Could not delete file: {delete_error}")
                
                uploaded_files.append(file_info)
                
            else:
                failed_uploads.append(file.filename if file else 'Unknown file')
        
        response_data = {
            'message': 'Upload completed',
            'uploadedCount': len(uploaded_files),
            'uploadedFiles': uploaded_files
        }
        
        if failed_uploads:
            response_data['failedFiles'] = failed_uploads
            response_data['message'] += f' ({len(failed_uploads)} files failed)'
        
        # Clean up old images to maintain max of 5 images
        cleanup_old_images(max_images=5)
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/files')
def list_files():
    """List all uploaded files"""
    try:
        files = []
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.isfile(file_path):
                file_info = {
                    'filename': filename,
                    'size': os.path.getsize(file_path),
                    'upload_time': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                }
                files.append(file_info)
        
        return jsonify({'files': files})
        
    except Exception as e:
        return jsonify({'error': f'Failed to list files: {str(e)}'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Download a specific file"""
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404

@app.route('/uploads/<filename>')
def serve_uploaded_image(filename):
    """Serve uploaded images"""
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except FileNotFoundError:
        return jsonify({'error': 'Image not found'}), 404

@app.route('/get_themes/<artwork_name>')
def get_artwork_themes(artwork_name):
    """Get themes for a specific artwork using the Agent"""
    try:
        # Initialize agent with the artwork name
        artwork_agent = Agent("artwork", artwork_name)
        artwork_agent.add_artwork_to_prompt()
        
        # Get details from the agent
        response = artwork_agent.get_details()
        
        return jsonify({
            'artwork_name': artwork_name,
            'themes': response,
            'success': True
        })
        
    except Exception as e:
        print(f"Error getting themes for {artwork_name}: {str(e)}")
        return jsonify({
            'artwork_name': artwork_name,
            'themes': f"Error analyzing themes: {str(e)}",
            'success': False
        }), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 413

if __name__ == '__main__':
    print("Starting GatorHacks4 File Upload Server...")
    print("Upload folder:", os.path.abspath(UPLOAD_FOLDER))
    print("Access the upload page at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
