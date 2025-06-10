import os
import django
from datetime import datetime, timedelta, time
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from venues.models import Venue, VenueAvailability


def clear_existing_data():
    """Clear existing venue data"""
    print("Clearing existing venue data...")
    VenueAvailability.objects.all().delete()
    Venue.objects.all().delete()
    print("✓ Existing data cleared.")


def create_venues(count=25):
    """Create sample venues"""
    print(f"Creating {count} venues...")

    venue_data = [
        {
            'name': 'Innovation Hub Conference Room',
            'description': 'Modern conference room with state-of-the-art presentation technology and collaborative tools.',
            'capacity': 25,
            'location': 'Building A, Floor 3',
            'category': 'conference',
            'features': {'projector': True, 'whiteboard': True, 'video_conferencing': True, 'wifi': True, 'coffee_station': True}
        },
        {
            'name': 'Executive Boardroom Alpha',
            'description': 'Premium boardroom with luxury furnishings and panoramic city views.',
            'capacity': 12,
            'location': 'Executive Plaza, Floor 10',
            'category': 'boardroom',
            'features': {'smart_board': True, 'audio_system': True, 'catering': True, 'natural_light': True, 'air_conditioning': True}
        },
        {
            'name': 'Creative Studio Space',
            'description': 'Flexible creative workspace designed for brainstorming and design thinking sessions.',
            'capacity': 16,
            'location': 'Creative Quarter, Floor 2',
            'category': 'meeting',
            'features': {'whiteboard': True, 'natural_light': True, 'wifi': True, 'coffee_station': True, 'printer': True}
        },
        {
            'name': 'Tech Summit Hall',
            'description': 'Large event hall perfect for company-wide presentations and tech conferences.',
            'capacity': 200,
            'location': 'Conference Center, Main Hall',
            'category': 'event',
            'features': {'projector': True, 'audio_system': True, 'video_conferencing': True, 'recording': True, 'catering': True, 'parking': True}
        },
        {
            'name': 'Collaboration Pod Beta',
            'description': 'Intimate meeting space ideal for small team collaborations and agile workflows.',
            'capacity': 8,
            'location': 'Innovation Center, Floor 1',
            'category': 'meeting',
            'features': {'whiteboard': True, 'wifi': True, 'natural_light': True, 'coffee_station': True}
        },
        {
            'name': 'Digital Workshop Room',
            'description': 'High-tech training facility equipped with interactive learning tools and presentation systems.',
            'capacity': 30,
            'location': 'Training Institute, Floor 2',
            'category': 'conference',
            'features': {'projector': True, 'smart_board': True, 'audio_system': True, 'wifi': True, 'air_conditioning': True}
        },
        {
            'name': 'Strategic Planning Suite',
            'description': 'Executive-level meeting room designed for strategic discussions and decision-making.',
            'capacity': 15,
            'location': 'Corporate Tower, Floor 8',
            'category': 'boardroom',
            'features': {'projector': True, 'teleconference': True, 'catering': True, 'natural_light': True, 'wifi': True}
        },
        {
            'name': 'Networking Lounge',
            'description': 'Casual meeting space perfect for informal discussions and networking events.',
            'capacity': 40,
            'location': 'Business Complex - North, Floor 1',
            'category': 'event',
            'features': {'audio_system': True, 'catering': True, 'wifi': True, 'coffee_station': True, 'natural_light': True}
        },
        {
            'name': 'Training Center A',
            'description': 'Professional training facility with modular seating and comprehensive AV equipment.',
            'capacity': 50,
            'location': 'Training Institute, Floor 3',
            'category': 'conference',
            'features': {'projector': True, 'audio_system': True, 'wifi': True, 'air_conditioning': True, 'printer': True}
        },
        {
            'name': 'Presentation Theater',
            'description': 'Theater-style presentation room with tiered seating and professional lighting.',
            'capacity': 75,
            'location': 'Conference Center, Theater Wing',
            'category': 'event',
            'features': {'projector': True, 'audio_system': True, 'recording': True, 'air_conditioning': True, 'accessibility': True}
        },
        {
            'name': 'Brainstorming Lab',
            'description': 'Creative thinking space with moveable furniture and extensive whiteboard walls.',
            'capacity': 20,
            'location': 'Innovation Center, Floor 2',
            'category': 'meeting',
            'features': {'whiteboard': True, 'natural_light': True, 'wifi': True, 'coffee_station': True, 'projector': True}
        },
        {
            'name': 'Client Meeting Room',
            'description': 'Professional meeting room designed to impress clients with elegant furnishings.',
            'capacity': 10,
            'location': 'Business Complex - South, Floor 5',
            'category': 'meeting',
            'features': {'video_conferencing': True, 'catering': True, 'natural_light': True, 'wifi': True, 'air_conditioning': True}
        },
        {
            'name': 'Product Demo Space',
            'description': 'Specialized room for product demonstrations with flexible setup options.',
            'capacity': 35,
            'location': 'Technology Hub, Floor 1',
            'category': 'conference',
            'features': {'projector': True, 'smart_board': True, 'audio_system': True, 'wifi': True, 'recording': True}
        },
        {
            'name': 'Leadership Conference Hall',
            'description': 'Premium conference facility for executive meetings and leadership summits.',
            'capacity': 60,
            'location': 'Executive Plaza, Floor 12',
            'category': 'event',
            'features': {'projector': True, 'audio_system': True, 'video_conferencing': True, 'catering': True, 'parking': True}
        },
        {
            'name': 'Team Building Arena',
            'description': 'Spacious room designed for team building activities and group exercises.',
            'capacity': 45,
            'location': 'Main Campus - West Wing, Floor 1',
            'category': 'event',
            'features': {'audio_system': True, 'wifi': True, 'natural_light': True, 'air_conditioning': True, 'coffee_station': True}
        }
    ]

    # Additional venue names for remaining slots
    additional_names = [
        'Innovation Workshop', 'Executive Suite Premium', 'Focus Group Room',
        'Design Thinking Lab', 'Startup Pitch Deck', 'Corporate Training Hub',
        'Media Production Room', 'Collaboration Central', 'Think Tank Chamber',
        'Business Development Center', 'Remote Work Studio', 'Agile Sprint Room',
        'Customer Experience Lab', 'Data Analytics Suite', 'Future Tech Pavilion'
    ]

    locations = [
        'Building A, Floor 1', 'Building A, Floor 2', 'Building B, Floor 1',
        'Building B, Floor 2', 'Building C, Floor 1', 'Main Campus - East Wing',
        'Technology Hub', 'Research Facility', 'Digital Campus', 'Collaboration Hub'
    ]

    categories = ['conference', 'meeting', 'event', 'boardroom']

    feature_options = [
        'projector', 'whiteboard', 'video_conferencing', 'audio_system', 'wifi',
        'catering', 'parking', 'accessibility', 'natural_light', 'air_conditioning',
        'printer', 'coffee_station', 'smart_board', 'teleconference', 'recording'
    ]

    created_venues = []

    # Create venues from predefined data
    for i, data in enumerate(venue_data[:count]):
        venue = Venue.objects.create(
            name=data['name'],
            description=data['description'],
            capacity=data['capacity'],
            location=data['location'],
            category=data['category'],
            handled_by=random.choice(['sa', 'ppk']),
            is_available=random.choice([True, True, True, False]),  # 75% available
            requires_approval=random.choice([True, True, False]),   # 66% require approval
            requires_payment=data['capacity'] > 50 or data['category'] == 'event',
            requires_documents=data['capacity'] > 100 or random.choice([True, False]),
            features=data['features']
        )
        created_venues.append(venue)

    # Create additional random venues if needed
    for i in range(len(venue_data), count):
        capacity = random.choice([8, 12, 16, 20, 25, 30, 40, 50, 75, 100])
        category = random.choice(categories)

        # Generate random features
        selected_features = random.sample(feature_options, k=random.randint(3, 7))
        features_dict = {feature: True for feature in selected_features}

        venue = Venue.objects.create(
            name=additional_names[i % len(additional_names)],
            description=f'Professional {category} space with modern amenities and flexible configuration options.',
            capacity=capacity,
            location=random.choice(locations),
            category=category,
            handled_by=random.choice(['sa', 'ppk']),
            is_available=random.choice([True, True, True, False]),
            requires_approval=random.choice([True, True, False]),
            requires_payment=capacity > 50 or category == 'event',
            requires_documents=capacity > 100 or random.choice([True, False]),
            features=features_dict
        )
        created_venues.append(venue)

    print(f"✓ Created {len(created_venues)} venues.")
    return created_venues


def create_availability_schedules(venues):
    """Create availability schedules for venues"""
    print("Creating availability schedules...")

    # Generate availability for the next 60 days
    start_date = datetime.now().date()
    end_date = start_date + timedelta(days=60)

    time_slots = [
        (time(8, 0), time(10, 0)),   # 8:00-10:00
        (time(10, 0), time(12, 0)),  # 10:00-12:00
        (time(12, 0), time(14, 0)),  # 12:00-14:00
        (time(14, 0), time(16, 0)),  # 14:00-16:00
        (time(16, 0), time(18, 0)),  # 16:00-18:00
        (time(9, 0), time(12, 0)),   # 9:00-12:00
        (time(13, 0), time(17, 0)),  # 13:00-17:00
        (time(8, 0), time(17, 0)),   # 8:00-17:00 (full day)
    ]

    availability_count = 0

    for venue in venues:
        current_date = start_date

        while current_date <= end_date:
            # Skip some weekends
            if current_date.weekday() >= 5 and random.choice([True, False]):
                current_date += timedelta(days=1)
                continue

            # Randomly decide number of slots for this date
            num_slots = random.choices([0, 1, 2, 3, 4], weights=[15, 30, 35, 15, 5])[0]

            if num_slots > 0:
                selected_slots = random.sample(time_slots, min(num_slots, len(time_slots)))

                for start_time, end_time in selected_slots:
                    is_available = random.choices([True, False], weights=[75, 25])[0]

                    VenueAvailability.objects.create(
                        venue=venue,
                        date=current_date,
                        start_time=start_time,
                        end_time=end_time,
                        is_available=is_available
                    )
                    availability_count += 1

            current_date += timedelta(days=1)

    print(f"✓ Created {availability_count} availability slots.")


def print_summary():
    """Print database summary"""
    print("\n" + "="*50)
    print("DATABASE POPULATION COMPLETE")
    print("="*50)
    print(f"Total Venues: {Venue.objects.count()}")
    print(f"Total Availability Slots: {VenueAvailability.objects.count()}")
    print(f"Available Venues: {Venue.objects.filter(is_available=True).count()}")
    print("\nVenues by Category:")
    for category in ['conference', 'meeting', 'event', 'boardroom']:
        count = Venue.objects.filter(category=category).count()
        print(f"  - {category.title()}: {count}")
    print("\nVenues by Handler:")
    print(f"  - SA: {Venue.objects.filter(handled_by='sa').count()}")
    print(f"  - PPK: {Venue.objects.filter(handled_by='ppk').count()}")
    print("="*50)


if __name__ == "__main__":
    # Clear existing data (optional)
    user_input = input("Clear existing venue data? (y/N): ").lower()
    if user_input == 'y':
        clear_existing_data()

    # Create venues
    venue_count = input("Number of venues to create (default 25): ").strip()
    venue_count = int(venue_count) if venue_count.isdigit() else 25

    venues = create_venues(venue_count)
    create_availability_schedules(venues)
    print_summary()

    print("\n✅ Database population completed successfully!")