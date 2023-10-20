from django.test import TestCase
from django.utils import timezone
from market_place.constants import StorageTypes
from djmoney.money import Money
from market_place.models import Profile, StorageBox
from booking.models import Booking
from datetime import date, timedelta
from django.db import models

class StorageBoxesTestCase(TestCase):

    def setUp(self):
        # Create a test profile
        self.profile = Profile.objects.create(
            first_name="Test",
            last_name="User",
            email="test@example.com"
        )

        # Create two StorageBox instances with different surface areas
        self.box1 = StorageBox.objects.create(
            owner=self.profile,
            storage_type=StorageTypes.GARAGE_BOX,  # Use an actual value from your StorageTypes
            title='Box 1',
            slug='box-1',
            description='Description for Box 1',
            surface=10,
            # monthly_price=Money(100, 'EUR'),
            street_number='123',
            route='Test Route',
            postal_code='12345',
            city='Test City',
            image_1='path/to/image1.jpg',  # Provide actual paths
            image_2='path/to/image2.jpg',
            image_3='path/to/image3.jpg'
        )

        self.box2 = StorageBox.objects.create(
            owner=self.profile,
            storage_type=StorageTypes.CELLAR,  # Use an actual value from your StorageTypes
            title='Box 2',
            slug='box-2',
            description='Description for Box 2',
            surface=15,
            # monthly_price=Money(150, 'EUR'),
            street_number='124',
            route='Test Route 2',
            postal_code='12346',
            city='Test City 2',
            image_1='path/to/image4.jpg',  # Provide actual paths
            image_2='path/to/image5.jpg',
            image_3='path/to/image6.jpg'
        )

        start_date = timezone.now().date()
        end_date = start_date + timezone.timedelta(days=30)

        self.booking1 = Booking.objects.create(
            tenant=self.profile,
            start_date=date.today() - timedelta(days=5),
            end_date=date.today() + timedelta(days=10),
            storage_box=self.box1,
        )

        self.booking2 = Booking.objects.create(
            tenant=self.profile,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=15),
            storage_box=self.box2,
        )

    def test_boxes_display_order(self):
        # Test if boxes are displayed in the correct order based on the latest booking's start date
        latest_booked_storage = StorageBox.objects.annotate(
            latest_booking_date=models.Max('booking__start_date')
        ).order_by('-latest_booking_date').first()
        self.assertEqual(latest_booked_storage, self.box2)

    def test_filter_by_surface_area(self):
        # Test filtering boxes by surface area
        filtered_boxes = StorageBox.objects.filter(surface__gte=12)  # assuming `surface` is the correct field name
        self.assertEqual(len(filtered_boxes), 1)
        self.assertEqual(filtered_boxes[0], self.box2)

    def test_booking_creation(self):
        self.assertIsInstance(self.booking1, Booking)
        self.assertIsInstance(self.booking2, Booking)

    def test_multiple_bookings_for_profile(self):
        bookings_for_profile = Booking.objects.filter(tenant=self.profile)
        self.assertEqual(bookings_for_profile.count(), 2)

    def test_delete_storage_box_cascades_to_booking(self):
        self.box1.delete()
        bookings_for_storage1 = Booking.objects.filter(storage_box=self.box1)
        self.assertEqual(bookings_for_storage1.count(), 0)
