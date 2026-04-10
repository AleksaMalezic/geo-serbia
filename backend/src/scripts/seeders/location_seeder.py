from src.domains.games.models import LocationDifficultyProfile
from src.domains.locations.models import Location
from src.domains.users.models import User

TARGET_LOCATION_COUNT = 40

BASE_LOCATIONS = [
    {
        "name": "Golubac Fortress",
        "latitude": 44.6542,
        "longitude": 21.6356,
        "description": "Medieval fortress on the Danube river.",
        "hints": [
            "Na obali Dunava.",
            "Na ulazu u Djerdapsku klisuru."
        ]
    },
    {
        "name": "Djavolja Varos",
        "latitude": 42.9889,
        "longitude": 21.4133,
        "description": "Unique natural rock formations.",
        "hints": [
            "Prirodni fenomen na jugu Srbije.",
            "Kamene figure neobičnog oblika."
        ]
    },
    {
        "name": "Uvac Meanders",
        "latitude": 43.4333,
        "longitude": 19.8833,
        "description": "Famous river meanders and canyon.",
        "hints": [
            "Poznato po beloglavim supovima.",
            "Reka pravi velike krivine."
        ]
    },
    {
        "name": "Studenica Monastery",
        "latitude": 43.4875,
        "longitude": 20.5397,
        "description": "UNESCO-listed medieval monastery.",
        "hints": [
            "Jedan od najvažnijih manastira.",
            "Zadužbina Stefana Nemanje."
        ]
    },
    {
        "name": "Zica Monastery",
        "latitude": 43.7131,
        "longitude": 20.6947,
        "description": "Medieval monastery near Kraljevo.",
        "hints": [
            "Crvena fasada.",
            "Blizu Kraljeva."
        ]
    },
    {
        "name": "Oplenac Church",
        "latitude": 44.2542,
        "longitude": 20.6825,
        "description": "Royal mausoleum of the Karadjordjevic dynasty.",
        "hints": [
            "U Topoli.",
            "Porodica Karadjordjevic."
        ]
    },
    {
        "name": "Resava Cave",
        "latitude": 44.0625,
        "longitude": 21.5086,
        "description": "One of the most beautiful caves in Serbia.",
        "hints": [
            "Blizu Despotovca.",
            "Bogata pećinskim ukrasima."
        ]
    },
    {
        "name": "Petnica Cave",
        "latitude": 44.2750,
        "longitude": 19.9350,
        "description": "Cave near Valjevo.",
        "hints": [
            "U blizini Valjeva.",
            "Poznata istraživačka stanica u blizini."
        ]
    },
    {
        "name": "Lazarica Church",
        "latitude": 43.5833,
        "longitude": 21.3333,
        "description": "Medieval church in Krusevac.",
        "hints": [
            "U Krusevcu.",
            "Zadužbina kneza Lazara."
        ]
    },
    {
        "name": "Gamzigrad (Felix Romuliana)",
        "latitude": 43.9010,
        "longitude": 22.1970,
        "description": "Roman imperial palace complex.",
        "hints": [
            "UNESCO lokalitet.",
            "Blizu Zajecara."
        ]
    },

    {
        "name": "Tara National Park",
        "latitude": 43.8833,
        "longitude": 19.4167,
        "description": "Mountain park with dense forests.",
        "hints": [
            "Zapadna Srbija.",
            "Poznata po Pančićevoj omorici."
        ]
    },
    {
        "name": "Banjska Monastery",
        "latitude": 42.9990,
        "longitude": 20.8200,
        "description": "Medieval monastery in Kosovo region.",
        "hints": [
            "Zadužbina kralja Milutina.",
            "Blizu Zvecana."
        ]
    },
    {
        "name": "Smederevo Fortress",
        "latitude": 44.6633,
        "longitude": 20.9275,
        "description": "Large medieval fortress on Danube.",
        "hints": [
            "Na Dunavu.",
            "U Smederevu."
        ]
    },
    {
        "name": "Vrsac Tower",
        "latitude": 45.1167,
        "longitude": 21.3167,
        "description": "Ruins of medieval tower.",
        "hints": [
            "Na brdu iznad Vršca.",
            "Pogled na Banat."
        ]
    },
    {
        "name": "Subotica City Hall",
        "latitude": 46.1000,
        "longitude": 19.6667,
        "description": "Art Nouveau building.",
        "hints": [
            "U Subotici.",
            "Prepoznatljiva arhitektura."
        ]
    },
    {
        "name": "Palić Lake",
        "latitude": 46.1000,
        "longitude": 19.7667,
        "description": "Popular tourist lake.",
        "hints": [
            "Blizu Subotice.",
            "Poznato šetalište."
        ]
    },
    {
        "name": "Rajac Wine Cellars",
        "latitude": 43.7500,
        "longitude": 22.2167,
        "description": "Traditional wine village.",
        "hints": [
            "Istočna Srbija.",
            "Kamene vinske kuće."
        ]
    },
    {
        "name": "Drvengrad (Kustendorf)",
        "latitude": 43.7950,
        "longitude": 19.5110,
        "description": "Ethno village built by Emir Kusturica.",
        "hints": [
            "Na Mokroj Gori.",
            "Drveno selo."
        ]
    },
    {
        "name": "Sargan Eight Railway",
        "latitude": 43.7920,
        "longitude": 19.5200,
        "description": "Historic narrow-gauge railway.",
        "hints": [
            "Turistički voz.",
            "Krivudava pruga."
        ]
    },
    {
        "name": "Kopaonik National Park",
        "latitude": 43.2850,
        "longitude": 20.8050,
        "description": "Largest ski resort in Serbia.",
        "hints": [
            "Najpoznatiji ski centar.",
            "Centralna Srbija."
        ]
    },

    {
        "name": "Midzor Peak",
        "latitude": 43.3740,
        "longitude": 22.6210,
        "description": "Highest peak of Serbia.",
        "hints": [
            "Na Staroj planini.",
            "Najviša tačka Srbije."
        ]
    },
    {
        "name": "Stara Planina Waterfall Tupavica",
        "latitude": 43.3500,
        "longitude": 22.6000,
        "description": "Beautiful waterfall in eastern Serbia.",
        "hints": [
            "Na Staroj planini.",
            "Popularno mesto za fotografije."
        ]
    },
    {
        "name": "Manasija Fortress Walls",
        "latitude": 44.1015,
        "longitude": 21.4690,
        "description": "Fortified monastery complex.",
        "hints": [
            "Visoki bedemi.",
            "Kod Despotovca."
        ]
    },
    {
        "name": "Ada Ciganlija",
        "latitude": 44.7866,
        "longitude": 20.4135,
        "description": "Popular recreation area in Belgrade.",
        "hints": [
            "Veštačko jezero.",
            "U Beogradu."
        ]
    },
    {
        "name": "House on the Drina",
        "latitude": 43.9540,
        "longitude": 19.5670,
        "description": "Famous house on a rock in the river.",
        "hints": [
            "Kod Bajine Bašte.",
            "Na steni u reci."
        ]
    },

    {
        "name": "Krupaj Spring",
        "latitude": 44.1960,
        "longitude": 21.6870,
        "description": "Turquoise karst spring.",
        "hints": [
            "Istočna Srbija.",
            "Plava voda."
        ]
    },
    {
        "name": "Ravanica Monastery",
        "latitude": 43.9500,
        "longitude": 21.4333,
        "description": "Monastery of Prince Lazar.",
        "hints": [
            "Blizu Cuprije.",
            "Knez Lazar."
        ]
    },
    {
        "name": "Zlatibor Center",
        "latitude": 43.7240,
        "longitude": 19.7000,
        "description": "Tourist center on Zlatibor.",
        "hints": [
            "Planina Zlatibor.",
            "Popularno turističko mesto."
        ]
    },
    {
        "name": "Stopica Cave",
        "latitude": 43.6750,
        "longitude": 19.7500,
        "description": "Cave with terraces.",
        "hints": [
            "Kod Zlatibora.",
            "Kaskadne formacije."
        ]
    },
    {
        "name": "Gostilje Waterfall",
        "latitude": 43.6720,
        "longitude": 19.8020,
        "description": "Tall waterfall near Zlatibor.",
        "hints": [
            "Blizu Zlatibora.",
            "Vodopad u šumi."
        ]
    },

    {
        "name": "Sokobanja Spa",
        "latitude": 43.6440,
        "longitude": 21.8690,
        "description": "Famous spa town.",
        "hints": [
            "Poznata banja.",
            "Istočna Srbija."
        ]
    },
    {
        "name": "Rtanj Mountain",
        "latitude": 43.7700,
        "longitude": 21.9000,
        "description": "Pyramid-shaped mountain.",
        "hints": [
            "Neobičan oblik.",
            "Misteriozna planina."
        ]
    },
    {
        "name": "Maglic Fortress",
        "latitude": 43.5080,
        "longitude": 20.5340,
        "description": "Medieval fortress on hill.",
        "hints": [
            "Iznad reke Ibar.",
            "Blizu Kraljeva."
        ]
    },
    {
        "name": "Gradac Monastery",
        "latitude": 43.3590,
        "longitude": 20.6370,
        "description": "Serbian Orthodox monastery.",
        "hints": [
            "Zadužbina kraljice Jelene.",
            "Jugozapadna Srbija."
        ]
    },
    {
        "name": "Devil's Bridge (Vratna)",
        "latitude": 44.1600,
        "longitude": 22.3000,
        "description": "Natural stone arch.",
        "hints": [
            "Kod Negotina.",
            "Prirodni kameni luk."
        ]
    },

    {
        "name": "Vratna Gates",
        "latitude": 44.1605,
        "longitude": 22.3020,
        "description": "Series of natural stone arches.",
        "hints": [
            "Tri kamena mosta.",
            "Istočna Srbija."
        ]
    },
    {
        "name": "Iron Gate (Djerdap Gorge)",
        "latitude": 44.6833,
        "longitude": 22.5333,
        "description": "Largest gorge in Europe.",
        "hints": [
            "Na Dunavu.",
            "Granica sa Rumunijom."
        ]
    },
    {
        "name": "Lepenski Vir",
        "latitude": 44.5530,
        "longitude": 22.0250,
        "description": "Mesolithic archaeological site.",
        "hints": [
            "Praistorijsko naselje.",
            "Djerdap."
        ]
    },
    {
        "name": "Kladovo Fortress Fetislam",
        "latitude": 44.6080,
        "longitude": 22.6060,
        "description": "Ottoman fortress.",
        "hints": [
            "U Kladovu.",
            "Na Dunavu."
        ]
    },
    {
        "name": "Negotin Center",
        "latitude": 44.2260,
        "longitude": 22.5310,
        "description": "Town in eastern Serbia.",
        "hints": [
            "Istočna Srbija.",
            "Blizu granice."
        ]
    }
]


def _image_url(lat: float, lng: float) -> str:
    lat_s = f"{lat:.6f}"
    lng_s = f"{lng:.6f}"
    return (
        "https://staticmap.openstreetmap.de/staticmap.php"
        f"?center={lat_s},{lng_s}&zoom=12&size=1280x720&markers={lat_s},{lng_s},red-pushpin"
    )


def _all_locations() -> list[dict]:
    combined = [*BASE_LOCATIONS]
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
        f"Curated total: {len(locations)}, DB total: {total}"
    )
    