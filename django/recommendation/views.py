from django.shortcuts import render
from recommendation.recommendation import get_recommendations
from posts.models import ToDo

def index(request):
    recommendations = get_recommendations(request.user.id)
    recommended_items = ToDo.objects.filter(id__in=recommendations)
    return render(request, 'recommendations/recommended_todos.html', {'recommended_items': recommended_items},)