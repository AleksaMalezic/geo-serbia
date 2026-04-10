import re

from src.domains.games.models import LocationDifficultyProfile
from src.domains.locations.models import Location
from src.domains.users.models import User

TARGET_LOCATION_COUNT = 500

BASE_LOCATIONS = [
    {
        "name": "Manastir Manasija",
        "latitude": 44.1010,
        "longitude": 21.4696,
        "description": "Fortified medieval monastery near Despotovac.",
        "hints": [
            "Nalazi se u centralno-istocnoj Srbiji.",
            "U blizini je Resavska pecina.",
            "Srednjovekovni manastir sa utvrdjenjem.",
        ],
    },
    {
        "name": "Manastir Studenica",
        "latitude": 43.4867,
        "longitude": 20.5397,
        "description": "UNESCO-listed monastery founded in the 12th century.",
        "hints": [
            "U jugozapadnoj Srbiji je ova lokacija.",
            "Poznata je po belom mermeru.",
            "UNESCO kulturna bastina.",
        ],
    },
    {
        "name": "Manastir Zica",
        "latitude": 43.7040,
        "longitude": 20.6906,
        "description": "Historic Serbian Orthodox monastery near Kraljevo.",
        "hints": [
            "Blizu Kraljeva je lokacija.",
            "Istorijski vazan manastir Nemanjica.",
            "Poznata crvena fasada.",
        ],
    },
    {
        "name": "Manastir Sopocani",
        "latitude": 43.1280,
        "longitude": 20.4187,
        "description": "Famous monastery with medieval frescoes.",
        "hints": [
            "U blizini Novog Pazara.",
            "Poznat po freskama iz 13. veka.",
            "Nalazi se u Raskoj oblasti.",
        ],
    },
    {
        "name": "Manastir Ravanica",
        "latitude": 43.9447,
        "longitude": 21.5200,
        "description": "Important monastery associated with Prince Lazar.",
        "hints": [
            "U Pomoravlju je ova lokacija.",
            "Povezan je sa knezom Lazarom.",
            "Srednjovekovna zaduzbina.",
        ],
    },
    {
        "name": "Kopaonik",
        "latitude": 43.2850,
        "longitude": 20.8090,
        "description": "Serbia's largest mountain massif and ski center.",
        "hints": [
            "Najpoznatiji ski-centar u Srbiji.",
            "Planina na jugu zemlje.",
            "Nacionalni park i vrh Pancicev vrh.",
        ],
    },
    {
        "name": "Tara Mountain",
        "latitude": 43.9000,
        "longitude": 19.5000,
        "description": "National park known for dense forests and viewpoints.",
        "hints": [
            "Na zapadu Srbije, uz Drinu.",
            "Nacionalni park sa gustim sumama.",
            "Poznata po vidikovcu Banjska stena.",
        ],
    },
    {
        "name": "Stara Planina",
        "latitude": 43.3360,
        "longitude": 22.5780,
        "description": "Mountain range in eastern Serbia with diverse nature.",
        "hints": [
            "Na istoku Srbije, uz granicu sa Bugarskom.",
            "Poznata po slapovima i ski-stazama.",
            "Zove se i Balkan planina.",
        ],
    },
    {
        "name": "Zlatibor",
        "latitude": 43.7290,
        "longitude": 19.7020,
        "description": "Popular mountain destination in western Serbia.",
        "hints": [
            "Zapadna Srbija i planinski turizam.",
            "Poznat po gondoli i centru Zlatibor.",
            "U blizini su Uzice i Cajetina.",
        ],
    },
    {
        "name": "Rtanj",
        "latitude": 43.7770,
        "longitude": 21.8980,
        "description": "Distinct pyramidal mountain peak in eastern Serbia.",
        "hints": [
            "Planina piramidalnog oblika.",
            "Nalazi se kod Boljevca.",
            "Cesto vezana za mistiku i legende.",
        ],
    },
    {
        "name": "Belgrade Fortress (Kalemegdan)",
        "latitude": 44.8230,
        "longitude": 20.4500,
        "description": "Historic fortress overlooking the Sava and Danube.",
        "hints": [
            "U Beogradu na uscu dve reke.",
            "Pogled na Savu i Dunav.",
            "Jedna od najpoznatijih tvrdjava u Srbiji.",
        ],
    },
    {
        "name": "Saint Sava Temple",
        "latitude": 44.7983,
        "longitude": 20.4691,
        "description": "One of the largest Orthodox churches in the world.",
        "hints": [
            "Hram u centralnom delu Beograda.",
            "Nalazi se na Vracaru.",
            "Jedan od najvecih pravoslavnih hramova.",
        ],
    },
    {
        "name": "Novi Sad Petrovaradin Fortress",
        "latitude": 45.2526,
        "longitude": 19.8641,
        "description": "Iconic Danube fortress known for EXIT festival.",
        "hints": [
            "Nalazi se preko puta Novog Sada.",
            "Domacina je EXIT festivala.",
            "Na obali Dunava u Vojvodini.",
        ],
    },
    {
        "name": "Golubac Fortress",
        "latitude": 44.6580,
        "longitude": 21.6360,
        "description": "Medieval fortress on the Danube riverbank.",
        "hints": [
            "Tvrdjava na Dunavu.",
            "Nalazi se na ulazu u Djerdapsku klisuru.",
            "Istocna Srbija.",
        ],
    },
    {
        "name": "Nis Fortress",
        "latitude": 43.3190,
        "longitude": 21.8958,
        "description": "Ottoman-era fortress in the center of Nis.",
        "hints": [
            "U centru Nisa.",
            "Tvrdjava iz osmanskog perioda.",
            "Jugoistok Srbije.",
        ],
    },
    {
        "name": "Skull Tower (Cele Kula)",
        "latitude": 43.3129,
        "longitude": 21.9224,
        "description": "Unique historic monument from the 19th century.",
        "hints": [
            "Spomenik iz Prvog srpskog ustanka.",
            "Nalazi se u Nisu.",
            "Poznat i kao Cele kula.",
        ],
    },
    {
        "name": "Avala Tower",
        "latitude": 44.6960,
        "longitude": 20.5140,
        "description": "Telecommunication tower with panoramic city views.",
        "hints": [
            "Na planini Avali.",
            "Vidikovac juzno od Beograda.",
            "Prepoznatljiv TV toranj.",
        ],
    },
    {
        "name": "Viminacium",
        "latitude": 44.7360,
        "longitude": 21.2180,
        "description": "Archaeological site of a Roman city and legion camp.",
        "hints": [
            "Rimski arheoloski lokalitet.",
            "U blizini Kostolca.",
            "Istocna Srbija uz Dunav.",
        ],
    },
    {
        "name": "Gamzigrad (Felix Romuliana)",
        "latitude": 43.8930,
        "longitude": 22.1870,
        "description": "UNESCO Roman imperial palace near Zajecar.",
        "hints": [
            "UNESCO lokalitet kod Zajecara.",
            "Rimska carska palata.",
            "Istocna Srbija.",
        ],
    },
    {
        "name": "Drina House (Kucica na Drini)",
        "latitude": 43.9555,
        "longitude": 19.5711,
        "description": "Famous small house on a rock in the Drina river.",
        "hints": [
            "Mala kucica na steni u reci.",
            "Kod Bajine Baste.",
            "Zapadna Srbija, reka Drina.",
        ],
    },
]

CITY_CENTERS = [
    ("Belgrade", 44.8125, 20.4612, "severna centralna Srbija"),
    ("Novi Sad", 45.2671, 19.8335, "Vojvodina"),
    ("Nis", 43.3209, 21.8958, "jugoistocna Srbija"),
    ("Kragujevac", 44.0128, 20.9114, "Sumadija"),
    ("Subotica", 46.1000, 19.6667, "sever Vojvodine"),
    ("Uzice", 43.8586, 19.8488, "zapadna Srbija"),
    ("Kraljevo", 43.7236, 20.6873, "Raska oblast"),
    ("Novi Pazar", 43.1367, 20.5169, "jugozapadna Srbija"),
    ("Zrenjanin", 45.3836, 20.3894, "Banat"),
    ("Sombor", 45.7742, 19.1122, "backa ravnica"),
    ("Vranje", 42.5510, 21.9003, "krajnji jug Srbije"),
    ("Pozarevac", 44.6218, 21.1878, "Branicevski okrug"),
    ("Valjevo", 44.2751, 19.8982, "Kolubarski okrug"),
    ("Pirot", 43.1531, 22.5867, "jugoistok Srbije"),
    ("Cacak", 43.8914, 20.3497, "Moravicki okrug"),
    ("Kikinda", 45.8294, 20.4662, "severni Banat"),
    ("Leskovac", 42.9981, 21.9461, "Jablanicki okrug"),
    ("Loznica", 44.5319, 19.2258, "zapad Srbije"),
    ("Bor", 44.0749, 22.0959, "istocna Srbija"),
    ("Sremska Mitrovica", 44.9772, 19.6122, "Srem"),
    ("Krusevac", 43.5800, 21.3339, "Rasinski okrug"),
    ("Jagodina", 43.9771, 21.2612, "Pomoravski okrug"),
    ("Smederevo", 44.6644, 20.9276, "Podunavski okrug"),
    ("Sabac", 44.7467, 19.6900, "Macvanski okrug"),
    ("Prijepolje", 43.3897, 19.6481, "jugozapad Srbije"),
]

PLACE_TYPES = [
    ("City Center", "city district", "Urbana zona sa prepoznatljivim centrom."),
    ("Main Square", "city square", "Centralni gradski trg i pesacka zona."),
    ("Historic Building", "famous building", "Istorijska gradska gradjevina."),
    ("Cultural Center", "famous building", "Kulturna ustanova sa prepoznatljivom arhitekturom."),
    ("Orthodox Church", "famous building", "Verski objekat sa karakteristicnom kupolom."),
    ("Clock Tower", "monument", "Gradski simbol i istorijska kula sa satom."),
    ("Memorial Complex", "monument", "Spomen-kompleks znacajan za istoriju Srbije."),
    ("Monument Park", "monument", "Park sa centralnim spomenikom."),
    ("Ancient Fortress", "monument", "Utvrdjenje sa pogledom na grad ili reku."),
    ("Stone Bridge", "monument", "Istorijski most preko reke."),
    ("River Walk", "nature", "Setaliste uz reku i gradski kej."),
    ("Lake Shore", "nature", "Prirodna lokacija uz jezero ili akumulaciju."),
    ("Forest Trail", "nature", "Sumska staza i izletnicka zona."),
    ("Mountain Viewpoint", "nature", "Vidikovac sa panoramskim pogledom."),
    ("Cave Entrance", "nature cave", "Pecinski ulaz i kraski reljef."),
    ("Waterfall", "nature waterfall", "Prirodni vodopad i stenoviti teren."),
    ("River Canyon", "nature canyon", "Klisura i recni tok kroz stene."),
    ("Nature Reserve", "nature", "Zasticeno podrucje sa bogatom florom."),
]


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _image_url(lat: float, lng: float) -> str:
    lat_s = f"{lat:.6f}"
    lng_s = f"{lng:.6f}"
    return (
        "https://staticmap.openstreetmap.de/staticmap.php"
        f"?center={lat_s},{lng_s}&zoom=12&size=1280x720&markers={lat_s},{lng_s},red-pushpin"
    )


def _generated_locations() -> list[dict]:
    generated = []
    needed = max(TARGET_LOCATION_COUNT - len(BASE_LOCATIONS), 0)
    for idx in range(needed):
        city, lat, lng, region = CITY_CENTERS[idx % len(CITY_CENTERS)]
        label, category, desc = PLACE_TYPES[idx % len(PLACE_TYPES)]
        serial = idx // len(CITY_CENTERS) + 1

        lat_offset = (((idx * 37) % 23) - 11) * 0.012
        lng_offset = (((idx * 29) % 21) - 10) * 0.015

        location_name = f"{city} {label} {serial:02d}"
        location_lat = max(41.85, min(46.25, lat + lat_offset))
        location_lng = max(18.80, min(23.10, lng + lng_offset))

        generated.append(
            {
                "name": location_name,
                "latitude": round(location_lat, 6),
                "longitude": round(location_lng, 6),
                "description": f"{desc} Seeded location near {city} ({region}). Category: {category}.",
                "hints": [
                    f"Lokacija je blizu grada {city}.",
                    f"Pripada tipu lokacije: {category}.",
                    f"Trazi u regionu: {region}.",
                ],
            }
        )
    return generated


def _all_locations() -> list[dict]:
    combined = [*BASE_LOCATIONS, *_generated_locations()]
    for item in combined:
        item["image_url"] = _image_url(float(item["latitude"]), float(item["longitude"]))
        item["hints"] = (item.get("hints") or [])[:3]
    return combined


async def seed():
    creator = await User.filter(username="geo_admin").first()
    if not creator:
        creator = await User.first()

    if not creator:
        print("Locations skipped. No users available for created_by.")
        return

    locations = _all_locations()
    existing = {loc.name: loc for loc in await Location.all()}

    created_count = 0
    updated_count = 0
    for loc in locations:
        current = existing.get(loc["name"])
        if current:
            changed = False
            for field in ("description", "latitude", "longitude", "image_url", "hints"):
                if getattr(current, field) != loc[field]:
                    setattr(current, field, loc[field])
                    changed = True
            if not current.is_approved:
                current.is_approved = True
                changed = True
            if changed:
                await current.save()
                updated_count += 1
            continue

        await Location.create(
            name=loc["name"],
            description=loc["description"],
            latitude=loc["latitude"],
            longitude=loc["longitude"],
            image_url=loc["image_url"],
            hints=loc["hints"],
            created_by=creator,
            is_approved=True,
        )
        created_count += 1

    all_locations = await Location.all().order_by("id")
    total = len(all_locations)
    if total:
        for idx, location in enumerate(all_locations):
            ratio = idx / max(total - 1, 1)
            difficulty = 20.0 + ratio * 65.0
            profile = await LocationDifficultyProfile.filter(location_id=location.id).first()
            if not profile:
                await LocationDifficultyProfile.create(
                    location_id=location.id,
                    difficulty_rating=difficulty,
                    global_avg_distance_km=40.0 + ratio * 120.0,
                    global_avg_points=4500.0 - ratio * 3500.0,
                    attempt_count=20,
                )
            else:
                profile.difficulty_rating = difficulty
                profile.global_avg_distance_km = 40.0 + ratio * 120.0
                profile.global_avg_points = 4500.0 - ratio * 3500.0
                profile.attempt_count = max(int(profile.attempt_count or 0), 20)
                await profile.save()

    print(
        f"Locations seeded. Created: {created_count}, Updated: {updated_count}, "
        f"Total target: {TARGET_LOCATION_COUNT}, Categories: {len(PLACE_TYPES)}"
    )
