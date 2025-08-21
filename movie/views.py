from django.shortcuts import render
from django.http import HttpResponse
import matplotlib.pyplot as plt
import matplotlib
import io
import urllib, base64

from .models import Movie

# Create your views here.

def home(request):
    # código HTML en views :(
    # return HttpResponse('<h1>Welcome to Home Page</h1>')
    
    #uso de plantilla sin parámetros
    #return render(request, 'home.html')

    # uso de plantilla con parámetros
    #return render(request, 'home.html', {'name':'Paola Vallejo'})

    # búsqueda de películas
    searchTerm = request.GET.get('searchMovie')

    # si se está buscando una película
    if searchTerm:
        # lista únicamente la(s) película(s) cuyo título contiene el nombre buscado
        movies = Movie.objects.filter(title__icontains=searchTerm)
    else: 
        # lista todas las películas de la base de datos
        movies = Movie.objects.all()
    return render(request, 'home.html', {'searchTerm':searchTerm, 'movies': movies})



 # Función para 'About'
def about(request):
    #return HttpResponse('<h1>Welcome to About Page</h1>')
   
    #uso de plantilla sin parámetros
    return render(request, 'about.html')

def signup(request):
    email = None
    if request.method == "POST":   
        email = request.POST.get('email')
        
    return render(request, 'signup.html', {'email': email})


def statistics_view(request):
    matplotlib.use('Agg')

    movies = Movie.objects.all()

    # ========= CONTADOR POR GÉNERO =========
    counts_by_genre = {}
    for m in movies:
        raw = (m.genre or "").strip()
        if not raw:
            counts_by_genre["None"] = counts_by_genre.get("None", 0) + 1
            continue
        for g in [x.strip() for x in raw.split(",") if x.strip()]:
            counts_by_genre[g] = counts_by_genre.get(g, 0) + 1

    # Ordenar por frecuencia y quedarnos con el Top N
    TOP_N = 12
    sorted_genres = sorted(counts_by_genre.items(), key=lambda kv: kv[1], reverse=True)[:TOP_N]
    genres = [g for g, _ in sorted_genres]
    genre_counts = [c for _, c in sorted_genres]

    # ---- Gráfica por género  ----
    plt.figure(figsize=(10, 6))
    x_pos = range(len(genres))
    plt.bar(x_pos, genre_counts, width=0.6)
    plt.xticks(x_pos, genres, rotation=45, ha='right')
    plt.title('Movies per genre (Top {})'.format(TOP_N))
    plt.xlabel('Genre')
    plt.ylabel('Number of movies')
    # Anotar valores sobre cada barra
    for x, v in enumerate(genre_counts):
        plt.text(x, v + 0.2, str(v), ha='center', va='bottom', fontsize=8)
    plt.tight_layout()

    buf1 = io.BytesIO()
    plt.savefig(buf1, format='png')
    buf1.seek(0)
    plt.close()
    graphic_genre = base64.b64encode(buf1.getvalue()).decode('utf-8')
    buf1.close()

    # ========= CONTADOR POR AÑO =========
    counts_by_year = {}
    for m in movies:
        year = m.year if m.year else "None"
        counts_by_year[year] = counts_by_year.get(year, 0) + 1

    numeric_years = sorted([y for y in counts_by_year if isinstance(y, int)])
    tail = [y for y in counts_by_year if not isinstance(y, int)]
    years = numeric_years + tail
    year_counts = [counts_by_year[y] for y in years]

    # ---- Gráfica por año ----
    plt.figure(figsize=(11, 5))
    x_pos = range(len(years))
    plt.bar(x_pos, year_counts, width=0.6)
    plt.title('Movies per year')
    plt.xlabel('Year')
    plt.ylabel('Number of movies')
    plt.xticks(x_pos, years, rotation=45, ha='right')
    for x, v in enumerate(year_counts):
        plt.text(x, v + 0.2, str(v), ha='center', va='bottom', fontsize=8)
    plt.tight_layout()

    buf2 = io.BytesIO()
    plt.savefig(buf2, format='png')
    buf2.seek(0)
    plt.close()
    graphic_year = base64.b64encode(buf2.getvalue()).decode('utf-8')
    buf2.close()

    return render(
        request,
        'statistics.html',
        {
            'graphic_genre': graphic_genre,
            'graphic_year': graphic_year,
        }
    )

#-------------------------------------------------------------------------------------
# def statistics_view(request):
#     matplotlib.use('Agg')
#     years = Movie.objects.values_list('year', flat=True).distinct().order_by('year')  # Obtener todos los años de las películas
    
#     movie_counts_by_year = {}  # Crear un diccionario para almacenar la cantidad de películas por año
#     for year in years:  # Contar la cantidad de películas por año
#         if year:
#             movies_in_year = Movie.objects.filter(year=year)
#         else:
#             movies_in_year = Movie.objects.filter(year__isnull=True)
#             year = "None"
#         count = movies_in_year.count()
#         movie_counts_by_year[year] = count

#     bar_width = 0.5   # Ancho de las barras
#     bar_spacing = 0.5 # Separación entre las barras
#     bar_positions = range(len(movie_counts_by_year))  # Posiciones de las barras
#     # Crear la gráfica de barras
#     plt.bar(bar_positions, movie_counts_by_year.values(), width=bar_width, align='center')

# # Personalizar la gráfica
#     plt.title('Movies per year')
#     plt.xlabel('Year')
#     plt.ylabel('Number of movies')
#     plt.xticks(bar_positions, movie_counts_by_year.keys(), rotation=90)

# # Ajustar el espaciado entre las barras
#     plt.subplots_adjust(bottom=0.3)

# # Guardar la gráfica en un objeto BytesIO
#     buffer = io.BytesIO()
#     plt.savefig(buffer, format='png')
#     buffer.seek(0)
#     plt.close()

# # Convertir la gráfica a base64
#     image_png = buffer.getvalue()
#     buffer.close()
#     graphic = base64.b64encode(image_png)
#     graphic = graphic.decode('utf-8')

# # Renderizar la plantilla statistics.html con la gráfica
#     return render(request, 'statistics.html', {'graphic': graphic})

# def statistics_view(request):
#     matplotlib.use('Agg')
#     # Obtener todas las películas
#     all_movies = Movie.objects.all()

#     # Crear un diccionario para almacenar la cantidad de películas por año
#     movie_counts_by_year = {}

#     # Filtrar las películas por año y contar la cantidad de películas por año
#     for movie in all_movies:
#         year = movie.year if movie.year else "None"
#         if year in movie_counts_by_year:
#             movie_counts_by_year[year] += 1
#         else:
#             movie_counts_by_year[year] = 1

#     # Ancho de las barras
#     bar_width = 0.5
#     # Posiciones de las barras
#     bar_positions = range(len(movie_counts_by_year))

#     # Crear la gráfica de barras
#     plt.bar(bar_positions, movie_counts_by_year.values(), width=bar_width, align='center')

#     # Personalizar la gráfica
#     plt.title('Movies per year')
#     plt.xlabel('Year')
#     plt.ylabel('Number of movies')
#     plt.xticks(bar_positions, movie_counts_by_year.keys(), rotation=90)

#     # Ajustar el espaciado entre las barras
#     plt.subplots_adjust(bottom=0.3)

#     # Guardar la gráfica en un objeto BytesIO
#     buffer = io.BytesIO()
#     plt.savefig(buffer, format='png')
#     buffer.seek(0)
#     plt.close()

#     # Convertir la gráfica a base64
#     image_png = buffer.getvalue()
#     buffer.close()
#     graphic = base64.b64encode(image_png)
#     graphic = graphic.decode('utf-8')

#     # Renderizar la plantilla statistics.html con la gráfica
#     return render(request, 'statistics.html', {'graphic': graphic})

