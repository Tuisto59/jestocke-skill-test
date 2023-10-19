from django.test import TestCase
from .models import StorageBox
class StorageBoxesTestCase(TestCase):
    def setUp(self):
        # Create sample data for testing
        self.box1 = StorageBox.objects.create(
            name='Box 1',
            surface_area=10.0,
            availability=True,
        )
        self.box2 = StorageBox.objects.create(
            name='Box 2',
            surface_area=15.0,
            availability=False,
        )

    def test_boxes_display_order(self):
        # Test if boxes are displayed in the correct order (latest first)
        latest_box = StorageBox.objects.first()
        self.assertEqual(latest_box, self.box2)

    def test_filter_by_surface_area(self):
        # Test filtering boxes by surface area
        filtered_boxes = StorageBox.objects.filter(surface_area__gte=12.0)
        self.assertEqual(len(filtered_boxes), 1)
        self.assertEqual(filtered_boxes[0], self.box2)

    def test_filter_by_availability(self):
        # Test filtering boxes by availability
        available_boxes = StorageBox.objects.filter(availability=True)
        self.assertEqual(len(available_boxes), 1)
        self.assertEqual(available_boxes[0], self.box1)
