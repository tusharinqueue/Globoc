"""
GSoC Globe — Org Data Generator
Run: python3 generate_orgs.py
Output: orgs.json (place in your data/ folder)
Fetches from: https://api.gsocorganizations.dev/organizations.json
"""

import json
import urllib.request

# ──────────────────────────────────────────────
# STEP 1: Fetch live data
# ──────────────────────────────────────────────
print("Fetching orgs from gsocorganizations.dev API...")
url = "https://api.gsocorganizations.dev/organizations.json"
with urllib.request.urlopen(url) as resp:
    raw = json.loads(resp.read())
print(f"  Fetched {len(raw)} organizations")

# ──────────────────────────────────────────────
# STEP 2: Category mapping
# ──────────────────────────────────────────────
CATEGORY_MAP = {
    "artificial intelligence": "AI/ML",
    "data and databases": "DevTools",
    "data": "DevTools",
    "development tools": "DevTools",
    "programming languages": "DevTools",
    "end user applications": "Web",
    "web": "Web",
    "security": "Security",
    "infrastructure and cloud": "Cloud",
    "cloud": "Cloud",
    "operating systems": "Cloud",
    "mobile applications": "Mobile",
    "mobile": "Mobile",
    "science and medicine": "Science",
    "science": "Science",
    "social": "Web",
    "media": "Web",
    "other": "DevTools",
    "education": "Education",
    "graphics/video/audio/virtual reality": "DevTools",
    "graphics": "DevTools",
}

def map_category(raw_cat):
    if not raw_cat:
        return "DevTools"
    key = raw_cat.lower().strip()
    for k, v in CATEGORY_MAP.items():
        if k in key:
            return v
    # check topics/technologies for AI/ML hint
    return "DevTools"

def infer_category_from_topics(raw_cat, topics, techs):
    cat = map_category(raw_cat)
    if cat != "DevTools":
        return cat
    all_hints = " ".join((topics or []) + (techs or [])).lower()
    if any(t in all_hints for t in ["machine learning", "deep learning", "neural", "ai", "nlp", "tensorflow", "pytorch", "computer vision"]):
        return "AI/ML"
    if any(t in all_hints for t in ["android", "ios", "mobile", "flutter", "swift", "kotlin", "react native"]):
        return "Mobile"
    if any(t in all_hints for t in ["education", "student", "learning platform", "curriculum", "school"]):
        return "Education"
    if any(t in all_hints for t in ["security", "fuzzing", "cryptography", "vulnerability", "pentest", "malware"]):
        return "Security"
    if any(t in all_hints for t in ["kubernetes", "docker", "cloud", "devops", "aws", "gcp", "azure", "ci/cd", "container"]):
        return "Cloud"
    if any(t in all_hints for t in ["biology", "genomics", "chemistry", "physics", "astronomy", "medicine", "bioinformatics", "climate"]):
        return "Science"
    if any(t in all_hints for t in ["web", "frontend", "react", "angular", "vue", "html", "css", "javascript", "node.js"]):
        return "Web"
    return "DevTools"

# ──────────────────────────────────────────────
# STEP 3: Headquarters lat/lng lookup
# (HQ city of the org's primary registered address or founding location)
# ──────────────────────────────────────────────
HQ_COORDS = {
    # USA
    "python software foundation": (42.3601, -71.0589, "USA"),
    "apache software foundation": (38.9072, -77.0369, "USA"),
    "mozilla": (37.3867, -122.0580, "USA"),
    "mozilla foundation": (37.3867, -122.0580, "USA"),
    "the linux foundation": (37.4419, -122.1430, "USA"),
    "linux foundation": (37.4419, -122.1430, "USA"),
    "wikimedia foundation": (37.7749, -122.4194, "USA"),
    "git": (34.0522, -118.2437, "USA"),
    "llvm compiler infrastructure": (37.3382, -121.8863, "USA"),
    "postgresql": (37.7749, -122.4194, "USA"),
    "owasp foundation": (38.9072, -77.0369, "USA"),
    "owasp": (38.9072, -77.0369, "USA"),
    "the tor project": (42.3601, -71.0589, "USA"),
    "tor project": (42.3601, -71.0589, "USA"),
    "numfocus": (30.2672, -97.7431, "USA"),
    "cncf": (37.7749, -122.4194, "USA"),
    "cloud native computing foundation": (37.7749, -122.4194, "USA"),
    "kubernetes": (37.4419, -122.1430, "USA"),
    "openmrs": (41.8827, -87.6233, "USA"),
    "sugar labs": (42.3601, -71.0589, "USA"),
    "sugarlabs": (42.3601, -71.0589, "USA"),
    "scikit-learn": (48.8566, 2.3522, "France"),
    "tensorflow": (37.4220, -122.0841, "USA"),
    "opencv": (37.3382, -121.8863, "USA"),
    "blender foundation": (52.3676, 4.9041, "Netherlands"),
    "r project": (48.2082, 16.3738, "Austria"),
    "r project for statistical computing": (48.2082, 16.3738, "Austria"),
    "julia language": (42.3601, -71.0942, "USA"),
    "the julia language": (42.3601, -71.0942, "USA"),
    "sympy": (52.2297, 21.0122, "Poland"),
    "mlpack": (41.0534, -85.1183, "USA"),
    "openastronomy": (51.5074, -0.1278, "UK"),
    "osgeo": (49.2827, -123.1207, "Canada"),
    "fossasia": (1.3521, 103.8198, "Singapore"),
    "rocket.chat": (-23.5505, -46.6333, "Brazil"),
    "inkscape": (37.7749, -122.4194, "USA"),
    "gimp": (52.5200, 13.4050, "Germany"),
    "gnu image manipulation program": (52.5200, 13.4050, "Germany"),
    "openstreetmap": (51.5074, -0.1278, "UK"),
    "freebsd": (37.7749, -122.4194, "USA"),
    "debian": (48.8566, 2.3522, "France"),
    "haiku": (48.1351, 11.5820, "Germany"),
    "catrobat": (47.0707, 15.4395, "Austria"),
    "processing foundation": (40.7128, -74.0060, "USA"),
    "fedora project": (50.0755, 14.4378, "Czech Republic"),
    "eclipse foundation": (50.8503, 4.3517, "Belgium"),
    "zulip": (42.3601, -71.0589, "USA"),
    "mifos initiative": (47.6062, -122.3321, "USA"),
    "moodle": (-31.9505, 115.8605, "Australia"),
    "apertium": (40.4168, -3.7038, "Spain"),
    "ccextractor": (41.3851, 2.1734, "Spain"),
    "ccextractor development": (41.3851, 2.1734, "Spain"),
    "mariadb foundation": (60.1699, 24.9384, "Finland"),
    "scipy": (34.0522, -118.2437, "USA"),
    "matplotlib": (41.8827, -87.6233, "USA"),
    "pytorch": (37.4220, -122.0841, "USA"),
    "hugging face": (48.8566, 2.3522, "France"),
    "onnx": (47.6062, -122.3321, "USA"),
    "networkx": (35.2271, -80.8431, "USA"),
    "jderobot": (40.4168, -3.7038, "Spain"),
    "ardupilot": (-33.8688, 151.2093, "Australia"),
    "oppia foundation": (37.7749, -122.4194, "USA"),
    "oppia": (37.7749, -122.4194, "USA"),
    "kicad eda": (47.6062, -122.3321, "USA"),
    "kicad": (47.6062, -122.3321, "USA"),
    "asyncapi initiative": (40.4168, -3.7038, "Spain"),
    "asyncapi": (40.4168, -3.7038, "Spain"),
    "chromium": (37.4220, -122.0841, "USA"),
    "flare": (38.9072, -77.0369, "USA"),
    "nixos foundation": (52.3676, 4.9041, "Netherlands"),
    "nixos": (52.3676, 4.9041, "Netherlands"),
    "aossie": (-27.4698, 153.0251, "Australia"),
    "aflplusplus": (48.1351, 11.5820, "Germany"),
    "aflplusplus (american fuzzy lop++)": (48.1351, 11.5820, "Germany"),
    "circuitverse": (12.9716, 77.5946, "India"),
    "matrix.org foundation": (51.5074, -0.1278, "UK"),
    "matrix": (51.5074, -0.1278, "UK"),
    "openwisp": (41.9028, 12.4964, "Italy"),
    "shogun": (52.5200, 13.4050, "Germany"),
    "rtems project": (35.6870, -105.9378, "USA"),
    "cern sft": (46.2044, 6.1432, "Switzerland"),
    "libreoffice": (52.5200, 13.4050, "Germany"),
    "the document foundation": (52.5200, 13.4050, "Germany"),
    "videolan": (48.8566, 2.3522, "France"),
    "kde": (52.5200, 13.4050, "Germany"),
    "gnome foundation": (42.3601, -71.0589, "USA"),
    "gnome": (42.3601, -71.0589, "USA"),
    "52°north spatial information research gmbh": (51.9607, 7.6261, "Germany"),
    "3dtk": (49.7944, 9.9302, "Germany"),
    "ardupilot": (-33.8688, 151.2093, "Australia"),
    "biomedical informatics emory university": (33.7490, -84.3880, "USA"),
    "boston university xia": (42.3505, -71.1054, "USA"),
    "casbin": (39.9042, 116.4074, "China"),
    "c2si": (6.9271, 79.8612, "Sri Lanka"),
    "chromium": (37.4220, -122.0841, "USA"),
    "deeppavlov": (55.7558, 37.6173, "Russia"),
    "eclipse foundation": (50.8503, 4.3517, "Belgium"),
    "einsteinpy": (28.6139, 77.2090, "India"),
    "erofs filesystem": (39.9042, 116.4074, "China"),
    "fossasia": (1.3521, 103.8198, "Singapore"),
    "gcp scanner": (37.4220, -122.0841, "USA"),
    "gdevelop": (48.8566, 2.3522, "France"),
    "gnutls": (60.1699, 24.9384, "Finland"),
    "halide": (37.4220, -122.0841, "USA"),
    "hazelcast": (37.7749, -122.4194, "USA"),
    "humanai": (40.7128, -74.0060, "USA"),
    "inclusive design institute": (43.6532, -79.3832, "Canada"),
    "institut für angewandte informatik (infai) e.v.": (51.3397, 12.3731, "Germany"),
    "kart project": (-36.8509, 174.7645, "New Zealand"),
    "nv access": (-27.4698, 153.0251, "Australia"),
    "netty": (35.6762, 139.6503, "Japan"),
    "nixos foundation": (52.3676, 4.9041, "Netherlands"),
    "openrefine": (37.7749, -122.4194, "USA"),
    "plan 9 foundation": (37.7749, -122.4194, "USA"),
    "project wikiloop": (37.4220, -122.0841, "USA"),
    "ruby on rails": (-33.8688, 151.2093, "Australia"),
    "stichting su2": (52.0116, 4.3571, "Netherlands"),
    "su2 foundation": (52.0116, 4.3571, "Netherlands"),
    "tla+": (47.6062, -122.3321, "USA"),
    "the monarch initiative": (37.7749, -122.4194, "USA"),
    "the openroad initiative": (37.4419, -122.1430, "USA"),
    "the rust foundation": (38.9072, -77.0369, "USA"),
    "rust foundation": (38.9072, -77.0369, "USA"),
    "urban energy systems laboratory empa": (47.3769, 8.5417, "Switzerland"),
    "waycrate": (59.3293, 18.0686, "Sweden"),
    "xiph.org foundation": (37.7749, -122.4194, "USA"),
    "mypy": (37.4220, -122.0841, "USA"),
    "openproject": (52.5200, 13.4050, "Germany"),
    "drupal": (51.2194, 4.4025, "Belgium"),
    "accord project": (40.7128, -74.0060, "USA"),
    "babel": (37.7749, -122.4194, "USA"),
    "arduino": (43.8777, 11.1023, "Italy"),
    "carbon language": (37.4220, -122.0841, "USA"),
    "cmu sphinx": (40.4437, -79.9428, "USA"),
    "cockpit project": (37.7749, -122.4194, "USA"),
    "data for the common good": (42.3601, -71.0589, "USA"),
    "frescobaldi": (52.3676, 4.9041, "Netherlands"),
    "gambit": (37.7749, -122.4194, "USA"),
    "ganeti": (37.4220, -122.0841, "USA"),
    "gnu image manipulation program": (52.5200, 13.4050, "Germany"),
    "inclusivedesigninstitute": (43.6532, -79.3832, "Canada"),
    "json schema": (37.7749, -122.4194, "USA"),
    "postman": (37.7749, -122.4194, "USA"),
    "prism model checker": (51.5074, -0.1278, "UK"),
    "ascend": (30.2672, -97.7431, "USA"),
    "archc": (-22.9068, -43.1729, "Brazil"),
    "cbmi@uthsc": (35.1495, -90.0490, "USA"),
    "frescobaldi": (52.3676, 4.9041, "Netherlands"),
    "humanai": (40.7128, -74.0060, "USA"),
    "open robot os (ros)": (37.4220, -122.0841, "USA"),
    "ros": (37.4220, -122.0841, "USA"),
    "the p4 language consortium": (37.4420, -122.1430, "USA"),
    "opendaylight": (37.3382, -121.8863, "USA"),
    "openage": (48.1351, 11.5820, "Germany"),
    "sugar labs": (42.3601, -71.0589, "USA"),
    "biojs": (51.5074, -0.1278, "UK"),
    "beagleboard.org": (37.7749, -122.4194, "USA"),
    "ceph foundation": (37.7749, -122.4194, "USA"),
    "coala": (52.5200, 13.4050, "Germany"),
    "conan.io": (52.5200, 13.4050, "Germany"),
    "debian": (48.8566, 2.3522, "France"),
    "dmlc": (37.4420, -122.1430, "USA"),
    "drupal": (51.2194, 4.4025, "Belgium"),
    "elastic": (37.7749, -122.4194, "USA"),
    "emscripten": (37.4220, -122.0841, "USA"),
    "freecad": (48.8566, 2.3522, "France"),
    "gcc": (37.7749, -122.4194, "USA"),
    "gem5": (37.7749, -122.4194, "USA"),
    "gentoo foundation": (37.7749, -122.4194, "USA"),
    "gfoss": (37.9838, 23.7275, "Greece"),
    "haskell.org": (37.7749, -122.0841, "USA"),
    "heaptrack": (48.1351, 11.5820, "Germany"),
    "hydra ecosystem": (42.3601, -71.0589, "USA"),
    "illumos": (37.7749, -122.4194, "USA"),
    "imagemagick": (37.7749, -122.4194, "USA"),
    "inter-actief": (52.2215, 6.8937, "Netherlands"),
    "internet archive": (37.7749, -122.4194, "USA"),
    "ion": (37.7749, -122.4194, "USA"),
    "jenkins": (37.7749, -122.4194, "USA"),
    "joomla": (37.7749, -122.4194, "USA"),
    "kibana": (37.7749, -122.4194, "USA"),
    "lmonad": (37.7749, -122.4194, "USA"),
    "lxde": (25.0478, 121.5318, "Taiwan"),
    "mb-system": (41.5238, -70.6711, "USA"),
    "mediawiki": (37.7749, -122.4194, "USA"),
    "metacpan": (51.5074, -0.1278, "UK"),
    "mininet wifi": (-22.9068, -43.1729, "Brazil"),
    "mixxx": (37.7749, -122.4194, "USA"),
    "moby/docker": (37.7749, -122.4194, "USA"),
    "mono project": (37.7749, -122.4194, "USA"),
    "ns-3": (35.2271, -80.8431, "USA"),
    "objectsecurity": (37.7749, -122.4194, "USA"),
    "omegat": (35.6762, 139.6503, "Japan"),
    "open genome informatics": (42.3601, -71.0589, "USA"),
    "open hatch": (42.3601, -71.0589, "USA"),
    "open mpi": (35.2271, -80.8431, "USA"),
    "open printing": (40.4406, -79.9959, "USA"),
    "open robotics": (37.4220, -122.0841, "USA"),
    "openembedded": (37.7749, -122.4194, "USA"),
    "openfoam": (51.5074, -0.1278, "UK"),
    "openintents": (40.7128, -74.0060, "USA"),
    "openlayers": (40.7128, -74.0060, "USA"),
    "openmined": (37.7749, -122.4194, "USA"),
    "openstacki": (37.7749, -122.4194, "USA"),
    "openstreetmap foundation": (51.5074, -0.1278, "UK"),
    "opensusetoo": (48.1351, 11.5820, "Germany"),
    "opensuse": (48.1351, 11.5820, "Germany"),
    "owasp": (38.9072, -77.0369, "USA"),
    "p5.js": (40.7128, -74.0060, "USA"),
    "p5js": (40.7128, -74.0060, "USA"),
    "palisadoes foundation": (17.9970, -76.7936, "Jamaica"),
    "parrot foundation": (52.3676, 4.9041, "Netherlands"),
    "pencil code": (37.4220, -122.0841, "USA"),
    "pgsoc": (37.7749, -122.4194, "USA"),
    "plone": (37.7749, -122.4194, "USA"),
    "polypheny": (47.5595, 7.5886, "Switzerland"),
    "purr data": (40.7128, -74.0060, "USA"),
    "quantlib": (51.5074, -0.1278, "UK"),
    "rails girls summer of code": (52.5200, 13.4050, "Germany"),
    "rbdl": (48.9960, 8.4031, "Germany"),
    "rdkit": (51.5074, -0.1278, "UK"),
    "rocket.chat": (-23.5505, -46.6333, "Brazil"),
    "rubygems": (37.7749, -122.4194, "USA"),
    "sagemath": (37.7749, -122.4194, "USA"),
    "scummvm": (52.3676, 4.9041, "Netherlands"),
    "shogun machine learning toolbox": (52.5200, 13.4050, "Germany"),
    "silk road": (39.9042, 116.4074, "China"),
    "spdx": (37.4419, -122.1430, "USA"),
    "squeak/smalltalk": (37.4220, -122.0841, "USA"),
    "stellar development foundation": (37.7749, -122.4194, "USA"),
    "stichting libreoffice": (52.5200, 13.4050, "Germany"),
    "sun": (37.4220, -122.0841, "USA"),
    "swift": (37.4220, -122.0841, "USA"),
    "tahoe-lafs": (37.7749, -122.4194, "USA"),
    "taskcoach": (52.3676, 4.9041, "Netherlands"),
    "theano": (45.5017, -73.5673, "Canada"),
    "timvideos": (-33.8688, 151.2093, "Australia"),
    "trizetto": (40.7128, -74.0060, "USA"),
    "ubuntu": (51.5074, -0.1278, "UK"),
    "unicode consortium": (37.3382, -121.8863, "USA"),
    "urbit": (37.7749, -122.4194, "USA"),
    "vlc": (48.8566, 2.3522, "France"),
    "voltha project": (37.7749, -122.4194, "USA"),
    "vtk": (40.7488, -73.9856, "USA"),
    "web3j": (51.5074, -0.1278, "UK"),
    "wine": (37.7749, -122.4194, "USA"),
    "wire": (52.5200, 13.4050, "Germany"),
    "wishket": (37.5665, 126.9780, "South Korea"),
    "x.org foundation": (37.4419, -122.1430, "USA"),
    "xen project": (51.5074, -0.1278, "UK"),
    "xiph.org": (37.7749, -122.4194, "USA"),
    "yocto project": (37.4419, -122.1430, "USA"),
    "zulip": (42.3601, -71.0589, "USA"),
    "beagleboard": (37.7749, -122.4194, "USA"),
    "berkman center for internet and society": (42.3601, -71.0589, "USA"),
    "bionetgen": (40.4437, -79.9428, "USA"),
    "boost c++ libraries": (37.7749, -122.4194, "USA"),
    "buildroot": (48.8566, 2.3522, "France"),
    "bzr": (-33.8688, 151.2093, "Australia"),
    "camunda": (52.5200, 13.4050, "Germany"),
    "cargo": (37.4220, -122.0841, "USA"),
    "catalyst": (40.7128, -74.0060, "USA"),
    "chapel": (37.4419, -122.1430, "USA"),
    "chapel language": (37.4419, -122.1430, "USA"),
    "check_mk": (48.1351, 11.5820, "Germany"),
    "ckeditor": (52.4064, 16.9252, "Poland"),
    "cloudcv": (40.7128, -74.0060, "USA"),
    "conda": (37.7749, -122.4194, "USA"),
    "crystal language": (40.7128, -74.0060, "USA"),
    "cython": (48.8566, 2.3522, "France"),
    "d foundation": (37.7749, -122.4194, "USA"),
    "dataverse": (42.3601, -71.0589, "USA"),
    "davmail": (48.8566, 2.3522, "France"),
    "dita open toolkit": (37.7749, -122.4194, "USA"),
    "dmlc apache mxnet": (37.4420, -122.1430, "USA"),
    "docker": (37.7749, -122.4194, "USA"),
    "dockstore": (49.2827, -123.1207, "Canada"),
    "drupal association": (51.2194, 4.4025, "Belgium"),
    "ecmascript": (37.4220, -122.0841, "USA"),
    "emcee": (42.3601, -71.0589, "USA"),
    "encode": (51.5074, -0.1278, "UK"),
    "enzyme": (37.7749, -122.4194, "USA"),
    "ergo": (47.3769, 8.5417, "Switzerland"),
    "ethereum foundation": (47.3769, 8.5417, "Switzerland"),
    "exa-project": (48.1351, 11.5820, "Germany"),
    "f-droid": (52.5200, 13.4050, "Germany"),
    "filament group": (42.3601, -71.0589, "USA"),
    "flatpak": (51.5074, -0.1278, "UK"),
    "fluentd": (37.7749, -122.4194, "USA"),
    "fluxcd": (37.7749, -122.4194, "USA"),
    "fortran-lang": (37.7749, -122.4194, "USA"),
    "freeipa": (35.2271, -80.8431, "USA"),
    "freeplane": (52.3676, 4.9041, "Netherlands"),
    "geopandas": (37.7749, -122.4194, "USA"),
    "gnupg": (52.5200, 13.4050, "Germany"),
    "go language": (37.4220, -122.0841, "USA"),
    "grpc": (37.4220, -122.0841, "USA"),
    "gstreamer": (48.8566, 2.3522, "France"),
    "hadoop": (37.7749, -122.4194, "USA"),
    "hdf group": (40.1020, -88.2272, "USA"),
    "homebrew": (37.7749, -122.4194, "USA"),
    "httpie": (37.7749, -122.4194, "USA"),
    "hypothesis": (51.5074, -0.1278, "UK"),
    "igalia": (43.3623, -8.4115, "Spain"),
    "internationalization (i18n)": (37.4220, -122.0841, "USA"),
    "ipython": (37.7749, -122.4194, "USA"),
    "istio": (37.4220, -122.0841, "USA"),
    "jabber.org": (37.7749, -122.4194, "USA"),
    "joplin": (48.8566, 2.3522, "France"),
    "jsonnet": (37.4220, -122.0841, "USA"),
    "jupyter": (37.7749, -122.4194, "USA"),
    "project jupyter": (37.7749, -122.4194, "USA"),
    "keycloak": (37.4220, -122.0841, "USA"),
    "knative": (37.4220, -122.0841, "USA"),
    "krita": (52.3676, 4.9041, "Netherlands"),
    "lapack": (37.7749, -122.4194, "USA"),
    "latte": (52.2297, 21.0122, "Poland"),
    "lean prover": (37.4220, -122.0841, "USA"),
    "libarchive": (37.7749, -122.4194, "USA"),
    "libav": (48.8566, 2.3522, "France"),
    "libcamera": (51.5074, -0.1278, "UK"),
    "libguestfs": (51.5074, -0.1278, "UK"),
    "libpeas": (37.7749, -122.4194, "USA"),
    "libreplan": (43.3623, -8.4115, "Spain"),
    "libvirt": (37.7749, -122.4194, "USA"),
    "lighttable": (37.7749, -122.4194, "USA"),
    "linkerd": (37.7749, -122.4194, "USA"),
    "lisp": (37.7749, -122.4194, "USA"),
    "lldb": (37.3382, -121.8863, "USA"),
    "lowrisc": (52.2053, 0.1218, "UK"),
    "lxc": (48.8566, 2.3522, "France"),
    "maas": (-33.8688, 151.2093, "Australia"),
    "mahara": (-41.2865, 174.7762, "New Zealand"),
    "mapnik": (51.5074, -0.1278, "UK"),
    "marlin firmware": (37.7749, -122.4194, "USA"),
    "massif": (48.8566, 2.3522, "France"),
    "mdanalysis": (37.7749, -122.4194, "USA"),
    "mediapipe": (37.4220, -122.0841, "USA"),
    "melange": (37.4220, -122.0841, "USA"),
    "memcached": (37.7749, -122.4194, "USA"),
    "mercurial": (48.8566, 2.3522, "France"),
    "mesa": (37.7749, -122.4194, "USA"),
    "metasploit": (37.7749, -122.4194, "USA"),
    "minc": (45.5017, -73.5673, "Canada"),
    "mint": (-33.8688, 151.2093, "Australia"),
    "mpd": (52.5200, 13.4050, "Germany"),
    "mumble": (52.5200, 13.4050, "Germany"),
    "mypy": (37.4220, -122.0841, "USA"),
    "ncl": (40.0150, -105.2705, "USA"),
    "neovim": (37.7749, -122.4194, "USA"),
    "nim language": (48.8566, 2.3522, "France"),
    "nmap": (37.7749, -122.4194, "USA"),
    "node.js": (37.7749, -122.4194, "USA"),
    "numpy": (37.7749, -122.4194, "USA"),
    "nwb": (37.7749, -122.4194, "USA"),
    "octave": (45.4215, -75.6972, "Canada"),
    "omeka": (38.9072, -77.0369, "USA"),
    "open3d": (37.4220, -122.0841, "USA"),
    "open bio": (42.3601, -71.0589, "USA"),
    "openbmc": (37.4220, -122.0841, "USA"),
    "openfst": (40.7128, -74.0060, "USA"),
    "opengate": (37.7749, -122.4194, "USA"),
    "openlibrary": (37.7749, -122.4194, "USA"),
    "openmotif": (37.7749, -122.4194, "USA"),
    "openmw": (37.7749, -122.4194, "USA"),
    "opennebula": (40.4168, -3.7038, "Spain"),
    "openssl": (51.5074, -0.1278, "UK"),
    "openstack": (37.7749, -122.4194, "USA"),
    "openvswitch": (37.4419, -122.1430, "USA"),
    "openvdb": (37.7749, -122.4194, "USA"),
    "orbit db": (37.7749, -122.4194, "USA"),
    "owncloud": (52.5200, 13.4050, "Germany"),
    "nextcloud": (48.1351, 11.5820, "Germany"),
    "papaparse": (40.7128, -74.0060, "USA"),
    "partial.js": (48.1486, 17.1077, "Slovakia"),
    "pelican": (48.8566, 2.3522, "France"),
    "photon": (37.4220, -122.0841, "USA"),
    "polarsys": (50.8503, 4.3517, "Belgium"),
    "poutine": (45.5017, -73.5673, "Canada"),
    "primesieve": (52.5200, 13.4050, "Germany"),
    "processhacker": (37.7749, -122.4194, "USA"),
    "puppet": (45.5231, -122.6765, "USA"),
    "pure data": (40.7128, -74.0060, "USA"),
    "pymc": (37.7749, -122.4194, "USA"),
    "pymc3": (37.7749, -122.4194, "USA"),
    "pymor": (48.1351, 11.5820, "Germany"),
    "pypy": (37.7749, -122.4194, "USA"),
    "qiskit": (37.7749, -122.4194, "USA"),
    "quantlib": (51.5074, -0.1278, "UK"),
    "qubes os": (52.2297, 21.0122, "Poland"),
    "redox os": (37.7749, -122.4194, "USA"),
    "robocomp": (40.4168, -3.7038, "Spain"),
    "rocketchat": (-23.5505, -46.6333, "Brazil"),
    "roughtime": (37.7749, -122.4194, "USA"),
    "rtems": (35.6870, -105.9378, "USA"),
    "ruby": (34.6937, 135.5022, "Japan"),
    "rust": (37.7749, -122.4194, "USA"),
    "selinux": (38.9072, -77.0369, "USA"),
    "signal": (37.7749, -122.4194, "USA"),
    "sigstore": (37.7749, -122.4194, "USA"),
    "simgrid": (48.8566, 2.3522, "France"),
    "socis": (52.2112, 4.4200, "Netherlands"),
    "soletta": (37.4220, -122.0841, "USA"),
    "spyder": (37.7749, -122.4194, "USA"),
    "squirrel sql": (37.7749, -122.4194, "USA"),
    "strace": (55.7558, 37.6173, "Russia"),
    "subversion": (37.7749, -122.4194, "USA"),
    "swift package manager": (37.4220, -122.0841, "USA"),
    "symbiflow": (37.7749, -122.4194, "USA"),
    "systemd": (52.5200, 13.4050, "Germany"),
    "taler": (46.2044, 6.1432, "Switzerland"),
    "tarantool": (55.7558, 37.6173, "Russia"),
    "taskwarrior": (37.7749, -122.4194, "USA"),
    "tcl tk": (37.7749, -122.4194, "USA"),
    "tensorflow extended": (37.4220, -122.0841, "USA"),
    "terraform": (37.7749, -122.4194, "USA"),
    "theano": (45.5017, -73.5673, "Canada"),
    "tidalcycles": (53.4808, -2.2426, "UK"),
    "tiled": (52.3676, 4.9041, "Netherlands"),
    "timescaledb": (40.7128, -74.0060, "USA"),
    "tokio": (37.4220, -122.0841, "USA"),
    "toolshed": (52.3676, 4.9041, "Netherlands"),
    "travis ci": (52.5200, 13.4050, "Germany"),
    "tugraph": (30.2741, 120.1551, "China"),
    "tvheadend": (48.1351, 11.5820, "Germany"),
    "twisted": (40.7128, -74.0060, "USA"),
    "ucsc genome browser": (36.9741, -122.0308, "USA"),
    "uima": (37.7749, -122.4194, "USA"),
    "umbrello uml modeller": (52.5200, 13.4050, "Germany"),
    "unixtree": (40.7128, -74.0060, "USA"),
    "unrealircd": (51.5074, -0.1278, "UK"),
    "urwid": (45.5017, -73.5673, "Canada"),
    "vala": (37.7749, -122.4194, "USA"),
    "valgrind": (51.5074, -0.1278, "UK"),
    "varnish cache": (59.9139, 10.7522, "Norway"),
    "vispy": (48.8566, 2.3522, "France"),
    "vital signs": (37.7749, -122.4194, "USA"),
    "vixl": (51.5074, -0.1278, "UK"),
    "vogon": (52.5200, 13.4050, "Germany"),
    "voidlinux": (37.7749, -122.4194, "USA"),
    "vpncloud": (48.1351, 11.5820, "Germany"),
    "wagtail": (51.5074, -0.1278, "UK"),
    "wayfire": (42.0000, 21.4333, "North Macedonia"),
    "weechat": (48.8566, 2.3522, "France"),
    "wildfly": (35.2271, -80.8431, "USA"),
    "winehq": (37.7749, -122.4194, "USA"),
    "wireshark": (37.7749, -122.4194, "USA"),
    "wpilib": (42.3601, -71.0589, "USA"),
    "wurstscript": (52.5200, 13.4050, "Germany"),
    "xapian": (51.5074, -0.1278, "UK"),
    "xen": (51.5074, -0.1278, "UK"),
    "xwiki": (48.8566, 2.3522, "France"),
    "yacy": (52.5200, 13.4050, "Germany"),
    "zephyr project": (37.4419, -122.1430, "USA"),
    "zimfw": (40.7128, -74.0060, "USA"),
    "zope foundation": (52.3676, 4.9041, "Netherlands"),
    "zuul": (37.7749, -122.4194, "USA"),
}

DEFAULT_COORDS_BY_TECH = {
    "java": (37.7749, -122.4194, "USA"),
    "python": (37.7749, -122.4194, "USA"),
}

def get_coords(name, technologies):
    key = name.lower().strip()
    # Try exact match
    if key in HQ_COORDS:
        return HQ_COORDS[key]
    # Try partial match
    for k, v in HQ_COORDS.items():
        if k in key or key in k:
            return v
    # Default to USA
    return (37.7749, -122.4194, "USA")

# ──────────────────────────────────────────────
# STEP 4: Tech stack cleaner
# ──────────────────────────────────────────────
def clean_stack(techs):
    if not techs:
        return ["Python"]
    cleaned = []
    rename = {
        "c": "C", "c++": "C++", "python": "Python", "java": "Java",
        "javascript": "JavaScript", "typescript": "TypeScript",
        "go": "Go", "rust": "Rust", "ruby": "Ruby", "php": "PHP",
        "scala": "Scala", "kotlin": "Kotlin", "swift": "Swift",
        "r": "R", "julia": "Julia", "haskell": "Haskell",
        "ocaml": "OCaml", "perl": "Perl", "lua": "Lua",
        "react": "React", "angular": "Angular", "vue.js": "Vue.js",
        "node.js": "Node.js", "django": "Django", "flask": "Flask",
        "spring": "Spring", "android": "Android", "ios": "iOS",
        "flutter": "Flutter", "docker": "Docker", "kubernetes": "Kubernetes",
        "tensorflow": "TensorFlow", "pytorch": "PyTorch", "cuda": "CUDA",
        "llvm": "LLVM", "clang": "Clang", "sql": "SQL",
        "postgresql": "PostgreSQL", "mysql": "MySQL", "git": "Git",
        "cmake": "CMake", "bash": "Bash", "shell": "Shell",
        "html": "HTML", "css": "CSS", "xml": "XML",
        "opencv": "OpenCV", "ros": "ROS", "qt": "Qt",
        "gtk": "GTK", "wxwidgets": "wxWidgets", "opengl": "OpenGL",
        "vulkan": "Vulkan", "webgl": "WebGL", "wasm": "WASM",
        "webassembly": "WebAssembly", "protobuf": "Protobuf",
        "grpc": "gRPC", "graphql": "GraphQL", "rest": "REST",
        "json": "JSON", "yaml": "YAML", "toml": "TOML",
        "numpy": "NumPy", "scipy": "SciPy", "cython": "Cython",
        "fortran": "Fortran", "assembly": "Assembly",
        "nix": "Nix", "ansible": "Ansible", "terraform": "Terraform",
    }
    seen = set()
    for t in techs[:8]:  # max 8 tags
        t_lower = t.lower().strip()
        mapped = rename.get(t_lower, t.strip().title())
        if mapped not in seen and len(mapped) > 1:
            cleaned.append(mapped)
            seen.add(mapped)
    return cleaned[:6] if cleaned else ["Python"]

# ──────────────────────────────────────────────
# STEP 5: Slug generator
# ──────────────────────────────────────────────
import re
def slugify(name):
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')

# ──────────────────────────────────────────────
# STEP 6: Transform all orgs
# ──────────────────────────────────────────────
output = []
seen_ids = set()

for org in raw:
    name = org.get("name", "").strip()
    if not name:
        continue

    years_dict = org.get("years", {})
    years_list = sorted([int(y) for y in years_dict.keys()])
    if not years_list:
        continue

    technologies = org.get("technologies", [])
    topics = org.get("topics", [])
    raw_cat = org.get("category", "")

    category = infer_category_from_topics(raw_cat, topics, technologies)
    lat, lng, country = get_coords(name, technologies)
    stack = clean_stack(technologies)

    # Estimate slots from historical data
    total_proj = sum(y.get("num_projects", 0) for y in years_dict.values())
    avg_slots = max(2, round(total_proj / len(years_list))) if years_list else 4

    # Build links
    org_url = org.get("url", "")
    org_id = slugify(name)
    # Avoid duplicate IDs
    if org_id in seen_ids:
        org_id = org_id + "-2"
    seen_ids.add(org_id)

    # Build gsoc page URL from most recent year's projects_url
    gsoc_page = ""
    if years_list:
        latest = str(max(years_list))
        latest_data = years_dict.get(latest, {})
        gsoc_page = latest_data.get("projects_url", "")

    # Try to find github URL
    github_url = ""
    for hint in [org_url]:
        if hint and "github.com" in hint:
            github_url = hint
            break
    if not github_url:
        # Make best guess
        github_url = f"https://github.com/{slugify(name)}"

    entry = {
        "id": org_id,
        "name": name,
        "category": category,
        "country": country,
        "lat": lat,
        "lng": lng,
        "years": years_list,
        "techStack": stack,
        "slots": avg_slots,
        "website": org_url or f"https://{slugify(name)}.org",
        "github": github_url,
        "gsocPage": gsoc_page or f"https://summerofcode.withgoogle.com/programs/2025/organizations/{org_id}"
    }
    output.append(entry)

print(f"Transformed {len(output)} organizations")

# Print category breakdown
cats = {}
for o in output:
    cats[o['category']] = cats.get(o['category'], 0) + 1
print("\nCategory breakdown:")
for k, v in sorted(cats.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")

# ──────────────────────────────────────────────
# STEP 7: Write output
# ──────────────────────────────────────────────
with open("orgs.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"\nDone! orgs.json written with {len(output)} organizations.")
print("Place it in your data/ folder.")
EOF