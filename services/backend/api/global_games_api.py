from unicodedata import category
from rest_framework.decorators import api_view
from ..model.game import Game
from ..serializers.game_serializers import GameSerializer
from django.http import HttpResponse
from rest_framework.response import Response

@api_view(['GET'])
def getGlobalDataTop(request):
    games = Game.objects.all().order_by('-rank')[:5] 
    serializer = GameSerializer(games, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getGlobalDataBottom(request):
    games = Game.objects.all().order_by('-rank').reverse()[:5] 
    serializer = GameSerializer(games, many=True)
    return Response(serializer.data)

from django.db import connection
@api_view(['GET'])
def getGlobalCategory(request):
    with connection.cursor() as cursor:
        cursor.execute("select sum(rank), category from backend_game group by category order by sum(rank) desc")
        rows = cursor.fetchall()
    categories = []
    i = 0
    for row in rows:
        i = i + 1
        category = {}
        category['id'] = i
        category['rank'] = row[0]
        category['category'] = row[1]
        categories.append(category)
        if i == 5:
            break
    return Response(categories)

@api_view(['GET'])
def getGlobalSubCategory(request):
    with connection.cursor() as cursor:
        cursor.execute("select sum(rank), subCategory from backend_game group by subCategory order by sum(rank) desc")
        rows = cursor.fetchall()
    subcategories = []
    i = 0
    for row in rows:
        i = i + 1
        subcategory = {}
        subcategory['id'] = i
        subcategory['rank'] = row[0]
        subcategory['category'] = row[1]
        subcategories.append(subcategory)
        if i == 5:
            break
    return Response(subcategories)

import random
@api_view(['POST'])
def updateBuy(request):
    gameId = request.data.get('gameId')
    
    try:
        game = Game.objects.get(gameId=gameId)
        if game.bought < 100:
            game.bought = game.bought + 1 
            game.viewed = game.viewed + 1 
            newRank = random.randint(0, 1000)
            game.rank = game.rank + (newRank / 100)
            game.save()
    except:
        game = None
        return HttpResponse("Internal error", status=500)
    if not game:
        return HttpResponse("No content", status=204)
    return Response("SUCCESS")