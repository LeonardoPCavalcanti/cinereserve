from django.test import TestCase

from apps.seats.models import Room, Seat


class RoomModelTest(TestCase):
    def setUp(self):
        self.room = Room.objects.create(
            name="Room 1",
            total_rows=10,
            seats_per_row=15,
        )

    def test_room_str(self):
        self.assertEqual(str(self.room), "Room 1")


class SeatModelTest(TestCase):
    def setUp(self):
        self.room = Room.objects.create(
            name="Room 1",
            total_rows=10,
            seats_per_row=15,
        )
        self.seat = Seat.objects.create(
            room=self.room,
            row="A",
            number=1,
        )

    def test_seat_label_computed_on_save(self):
        self.assertEqual(self.seat.seat_label, "A1")

    def test_seat_label_updates_on_change(self):
        self.seat.row = "B"
        self.seat.number = 5
        self.seat.save()
        self.assertEqual(self.seat.seat_label, "B5")

    def test_seat_str(self):
        self.assertEqual(str(self.seat), "Room 1 - A1")
