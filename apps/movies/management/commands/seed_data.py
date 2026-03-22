import random
import string
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.movies.models import Movie
from apps.seats.models import Room, Seat
from apps.sessions.models import CinemaSession


class Command(BaseCommand):
    help = "Seed database with initial data: movies, rooms, seats, and sessions"

    def handle(self, *args, **options):
        self.stdout.write("Seeding database...")

        movies = self._create_movies()
        rooms = self._create_rooms()
        self._create_sessions(movies, rooms)

        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))

    def _create_movies(self):
        movies_data = [
            {
                "title": "O Último Horizonte",
                "description": "Uma jornada épica através de galáxias desconhecidas em busca de um novo lar.",
                "duration_minutes": 148,
                "genre": "Ficção Científica",
                "director": "Ana Beatriz Costa",
                "cast": "Lucas Mendes, Carla Souza, Roberto Lima",
                "release_date": "2026-01-15",
            },
            {
                "title": "Sombras do Passado",
                "description": "Um detetive aposentado é forçado a revisitar o caso que destruiu sua carreira.",
                "duration_minutes": 127,
                "genre": "Suspense",
                "director": "Carlos Eduardo Ramos",
                "cast": "Fernando Alves, Juliana Pereira, André Moreira",
                "release_date": "2026-02-01",
            },
            {
                "title": "Amor em Código",
                "description": "Dois programadores rivais descobrem que o maior bug de suas vidas é o amor.",
                "duration_minutes": 105,
                "genre": "Comédia Romântica",
                "director": "Mariana Ferreira",
                "cast": "Thiago Santos, Isabela Oliveira",
                "release_date": "2026-02-14",
            },
            {
                "title": "A Floresta dos Espíritos",
                "description": "Uma família se muda para uma casa cercada por uma floresta de segredos.",
                "duration_minutes": 115,
                "genre": "Terror",
                "director": "Pedro Henrique Dias",
                "cast": "Camila Rocha, Daniel Almeida, Sofia Martins",
                "release_date": "2026-01-20",
            },
            {
                "title": "Velocidade Máxima 2",
                "description": "A equipe de corrida underground retorna para o maior desafio de suas vidas.",
                "duration_minutes": 132,
                "genre": "Ação",
                "director": "Ricardo Nunes",
                "cast": "Bruno Costa, Letícia Cardoso, Marcos Vieira",
                "release_date": "2026-03-01",
            },
            {
                "title": "O Pequeno Astronauta",
                "description": "Um garoto sonhador constrói um foguete e embarca numa aventura intergaláctica.",
                "duration_minutes": 95,
                "genre": "Animação",
                "director": "Fernanda Lima",
                "cast": "Vozes: Paulo Gustavo Jr., Maria Clara, João Pedro",
                "release_date": "2026-01-10",
            },
            {
                "title": "Revolução Silenciosa",
                "description": "Baseado em fatos reais, a história de um movimento de resistência na ditadura.",
                "duration_minutes": 155,
                "genre": "Drama",
                "director": "Gustavo Machado",
                "cast": "Renata Vasconcelos, Antônio Fagundes Jr., Clara Monteiro",
                "release_date": "2026-02-20",
            },
            {
                "title": "Dragões de Cristal",
                "description": "Em um reino medieval, uma jovem descobre que pode se comunicar com dragões ancestrais.",
                "duration_minutes": 140,
                "genre": "Fantasia",
                "director": "Bianca Torres",
                "cast": "Valentina Cruz, Rafael Borges, Helena Pinto",
                "release_date": "2026-03-10",
            },
            {
                "title": "O Golpe Perfeito",
                "description": "Uma equipe de ladrões planeja o roubo mais audacioso da história: o Banco Central.",
                "duration_minutes": 120,
                "genre": "Crime",
                "director": "Marcos Aurélio Silva",
                "cast": "Diego Ferraz, Patrícia Lemos, Vinícius Campos",
                "release_date": "2026-02-28",
            },
            {
                "title": "Memórias do Amanhã",
                "description": "Uma cientista inventa um dispositivo que permite ver memórias do futuro.",
                "duration_minutes": 138,
                "genre": "Ficção Científica",
                "director": "Laura Mendonça",
                "cast": "Gabriela Reis, Eduardo Nascimento, Tatiana Braga",
                "release_date": "2026-03-15",
            },
        ]

        movies = []
        for data in movies_data:
            movie, created = Movie.objects.get_or_create(title=data["title"], defaults=data)
            movies.append(movie)
            status = "Created" if created else "Already exists"
            self.stdout.write(f"  Movie: {movie.title} [{status}]")

        return movies

    def _create_rooms(self):
        rooms_data = [
            {"name": "Sala 1 - Standard", "total_rows": 8, "seats_per_row": 10},
            {"name": "Sala 2 - Premium", "total_rows": 8, "seats_per_row": 10},
            {"name": "Sala 3 - IMAX", "total_rows": 8, "seats_per_row": 10},
        ]

        rooms = []
        for data in rooms_data:
            room, created = Room.objects.get_or_create(name=data["name"], defaults=data)
            rooms.append(room)

            if created:
                self._create_seats_for_room(room)
                self.stdout.write(f"  Room: {room.name} [Created with {room.total_rows * room.seats_per_row} seats]")
            else:
                self.stdout.write(f"  Room: {room.name} [Already exists]")

        return rooms

    def _create_seats_for_room(self, room):
        row_letters = string.ascii_uppercase[: room.total_rows]
        seats = []
        for row in row_letters:
            for num in range(1, room.seats_per_row + 1):
                seats.append(
                    Seat(
                        room=room,
                        row=row,
                        number=num,
                        seat_label=f"{row}{num}",
                    )
                )
        Seat.objects.bulk_create(seats, ignore_conflicts=True)

    def _create_sessions(self, movies, rooms):
        now = timezone.now()
        formats_by_room = {
            0: "2D",
            1: "2D",
            2: "IMAX",
        }
        languages = ["Português", "Inglês Legendado", "Inglês Dublado"]

        session_count = 0
        for day_offset in range(7):
            day = now + timedelta(days=day_offset)
            base_times = [
                day.replace(hour=14, minute=0, second=0, microsecond=0),
                day.replace(hour=17, minute=0, second=0, microsecond=0),
                day.replace(hour=20, minute=0, second=0, microsecond=0),
            ]

            for room_idx, room in enumerate(rooms):
                movie = random.choice(movies)
                time_slot = base_times[room_idx % len(base_times)]
                fmt = formats_by_room.get(room_idx, "2D")
                lang = random.choice(languages)

                _, created = CinemaSession.objects.get_or_create(
                    room=room,
                    start_time=time_slot,
                    defaults={
                        "movie": movie,
                        "language": lang,
                        "format": fmt,
                    },
                )
                if created:
                    session_count += 1

        self.stdout.write(f"  Created {session_count} sessions across 7 days")
