from src.domains.locations.models import Location
from src.domains.users.models import User
from src.domains.games.models import LocationDifficultyProfile


LOCATIONS = [
    {"name": "Manastir Manasija", "latitude": 44.1010, "longitude": 21.4696, "description": "Fortified medieval monastery near Despotovac.", "image_url": "/static/uploads/locations/manastir-manasija-resava.jpg"},
    {"name": "Manastir Studenica", "latitude": 43.4867, "longitude": 20.5397, "description": "UNESCO-listed monastery founded in the 12th century.", "image_url": "/static/uploads/locations/studenica.jpg"},
    {"name": "Manastir Zica", "latitude": 43.7040, "longitude": 20.6906, "description": "Historic Serbian Orthodox monastery near Kraljevo.", "image_url": "/static/uploads/locations/zica.jpg"},
    {"name": "Manastir Sopocani", "latitude": 43.1280, "longitude": 20.4187, "description": "Famous monastery with medieval frescoes.", "image_url": "/static/uploads/locations/sopocani.jpg"},
    {"name": "Manastir Ravanica", "latitude": 43.9447, "longitude": 21.5200, "description": "Important monastery associated with Prince Lazar.", "image_url": "/static/uploads/locations/ravanica.jpg"},
    {"name": "Kopaonik", "latitude": 43.2850, "longitude": 20.8090, "description": "Serbia's largest mountain massif and ski center.", "image_url": "/static/uploads/locations/kopaonik.jpg"},
    {"name": "Tara Mountain", "latitude": 43.9000, "longitude": 19.5000, "description": "National park known for dense forests and viewpoints.", "image_url": "/static/uploads/locations/tara.jpg"},
    {"name": "Stara Planina", "latitude": 43.3360, "longitude": 22.5780, "description": "Mountain range in eastern Serbia with diverse nature.", "image_url": "/static/uploads/locations/stara-planina.jpg"},
    {"name": "Zlatibor", "latitude": 43.7290, "longitude": 19.7020, "description": "Popular mountain destination in western Serbia.", "image_url": "/static/uploads/locations/zlatibor.jpg"},
    {"name": "Rtanj", "latitude": 43.7770, "longitude": 21.8980, "description": "Distinct pyramidal mountain peak in eastern Serbia.", "image_url": "/static/uploads/locations/rtanj.png"},
    {"name": "Belgrade Fortress (Kalemegdan)", "latitude": 44.8230, "longitude": 20.4500, "description": "Historic fortress overlooking the Sava and Danube.", "image_url": "/static/uploads/locations/kalemegdan.webp"},
    {"name": "Saint Sava Temple", "latitude": 44.7983, "longitude": 20.4691, "description": "One of the largest Orthodox churches in the world.", "image_url": "/static/uploads/locations/hram-svetog-save.webp"},
    {"name": "Novi Sad Petrovaradin Fortress", "latitude": 45.2526, "longitude": 19.8641, "description": "Iconic Danube fortress known for EXIT festival.", "image_url": "/static/uploads/locations/petrovaradin.jpg"},
    {"name": "Golubac Fortress", "latitude": 44.6580, "longitude": 21.6360, "description": "Medieval fortress on the Danube riverbank.", "image_url": "/static/uploads/locations/golubac.jpg"},
    {"name": "Nis Fortress", "latitude": 43.3190, "longitude": 21.8958, "description": "Ottoman-era fortress in the center of Nis.", "image_url": "/static/uploads/locations/niska-tvrdjava.jpg"},
    {"name": "Skull Tower (Cele Kula)", "latitude": 43.3129, "longitude": 21.9224, "description": "Unique historic monument from the 19th century.", "image_url": "/static/uploads/locations/cele-kula.jpg"},
    {"name": "Avala Tower", "latitude": 44.6960, "longitude": 20.5140, "description": "Telecommunication tower with panoramic city views.", "image_url": "/static/uploads/locations/avalski-toranj.jpg"},
    {"name": "Viminacium", "latitude": 44.7360, "longitude": 21.2180, "description": "Archaeological site of a Roman city and legion camp.", "image_url": "/static/uploads/locations/viminacijum.jpg"},
    {"name": "Gamzigrad (Felix Romuliana)", "latitude": 43.8930, "longitude": 22.1870, "description": "UNESCO Roman imperial palace near Zajecar.", "image_url": "/static/uploads/locations/gamzigrad.jpg"},
    {"name": "Drina House (Kucica na Drini)", "latitude": 43.9555, "longitude": 19.5711, "description": "Famous small house on a rock in the Drina river.", "image_url": "/static/uploads/locations/kuca na drini.jpg"},
]


async def seed():
    # Prefer admin as creator for seeded public locations.
    creator = await User.filter(username="geo_admin").first()
    if not creator:
        creator = await User.first()

    if not creator:
        print("Locations skipped. No users available for created_by.")
        return

    existing = set(await Location.all().values_list("name", flat=True))
    created_count = 0

    for loc in LOCATIONS:
        if loc["name"] in existing:
            continue
        await Location.create(
            name=loc["name"],
            description=loc["description"],
            latitude=loc["latitude"],
            longitude=loc["longitude"],
            image_url=loc["image_url"],
            created_by=creator,
            is_approved=True,
        )
        created_count += 1

    # Seed deterministic difficulty spread for adaptive selection.
    # This gives all personas meaningful round mixes.
    all_locations = await Location.all().order_by("id")
    total = len(all_locations)
    if total:
        for idx, location in enumerate(all_locations):
            # Spread [20, 85] across locations.
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

    print(f"Locations seeded. Created: {created_count}")
