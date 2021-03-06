
import random
from tkinter import N
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
# from services.urls import MODEL_TREE, KNN_DATA, COLUMNS
from ..model.game import Game
from ..serializers.game_serializers import GameSerializer
import csv

@api_view(['GET'])
def getDummyData(request):
    games = [
        {"id": "0006b039-9d76-4bb2-80ed-89e228f7bdaa", "category": "A", "subCategory":"0", "price":"22.21"},
        {"id": "0002278b-67e3-406e-bfc2-63c48c195e2b", "category": "B", "subCategory":"1", "price":"54.43"},
        {"id": "0001c1dd-462e-453c-bac8-2fcdc0b0bc8d", "category": "C", "subCategory":"2", "price":"456.43"},
        {"id": "0006f0e4-d396-44b3-8fc1-0195a50a6660", "category": "A", "subCategory":"2", "price":"123.43"},
        {"id": "0002c59e-df87-47a8-a27d-26b34340bee5", "category": "A", "subCategory":"2", "price":"634.20"},
        {"id": "000362d7-cc2a-4912-b5ab-0b931e77942a", "category": "A", "subCategory":"3", "price":"65.76"},
        {"id": "000408f0-f0d0-447f-8700-30bb7dd390b1", "category": "D", "subCategory":"1", "price":"36.87"},
        {"id": "00045921-f5e7-40e0-bbb8-825474d0f7bc", "category": "B", "subCategory":"0", "price":"97.96"},
        {"id": "00048509-adaa-485e-bfcc-eee88b4aa08d", "category": "C", "subCategory":"2", "price":"53.32"},
    ]
    return Response(games)

@api_view(['GET'])
def gameList(request):
    try:
        places = Game.objects.all().order_by('-id')
    except:
        places = None
    if not places:
        return HttpResponse("No Content", status=404)
    serializer = GameSerializer(places, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def uploadData(request):
    try:
        file = open('items_2.csv')
        csvreader = csv.reader(file)
        rows = []
        for row in csvreader:
            rows.append(row)
        i=0
        for row in rows:
            if i < 70791:
                i = i + 1
                continue
            else:
                i = i + 1
                extractGame(row, i)   
    except Exception as e:
        print(e)
    return Response(None)

def extractGame(row, i):
    print(str(i) + " -> " + str(row))
    game = {}
    game['gameId'] = row[0]
    game['category'] = row[1]
    game['subCategory'] = row[2]
    game['price'] = row[3]
    game['bought'] = row[4]
    game['viewed'] = row[5]
    game['rank'] = 0.0
    serializer = GameSerializer(data=game)
    if serializer.is_valid():
        serializer.save()
    else:
        print(str(serializer.errors))


def getPrediction(game_id):
    game_row = KNN_DATA[KNN_DATA['product_id'] == game_id]
    game_row = game_row[COLUMNS]
    dist, ind = MODEL_TREE.query(game_row, k=6)
    product_ids = list()
    for j in ind[0][1:]:
        product_ids.append(KNN_DATA.loc[j]['product_id'])
    return product_ids

@api_view(['POST'])
def createPrediction(request):
    gameId = request.data.get('gameId')
    predictions = getPrediction(gameId)
    games = Game.objects.filter(gameId__in=predictions)
    for game in games:
        newRank = random.randint(0, 1000)
        game.rank = game.rank + (newRank / 100)
        game.save()
    game = Game.objects.get(gameId=gameId)
    newRank = random.randint(0, 1000)
    game.rank = game.rank + (newRank / 100)
    game.save()
    serializer = GameSerializer(games, many=True)
    return Response(serializer.data)

import pandas as pd
from sklearn.neighbors import KDTree

def loadModel():
    items = pd.read_csv("/home/app/webapp/services/KNN_dataset.csv")
    # items = pd.read_csv("KNN_dataset.csv")
    columns = items.columns[2:]
    X = items[columns]
    tree = KDTree(X)
    return tree
MODEL_TREE = loadModel()
KNN_DATA = pd.read_csv("/home/app/webapp/services/KNN_dataset.csv")
# KNN_DATA = pd.read_csv("KNN_dataset.csv")
COLUMNS = KNN_DATA.columns[2:]

@api_view(['POST'])
def getSuggestion(request):
    input = request.data.get('search')
    games = Game.objects.filter(gameId__startswith=input)[:5] 
    serializer = GameSerializer(games, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def fixRank(request):
    i = 0
    games = Game.objects.filter(rank=0)
    for game in games:
        i = i + 1
        newRank = random.randint(-150, 150)
        if i % 20 == 0:
            print(f"Updating {i}. out of {len(games)}, gameId = {game.gameId}, previous = {game.rank}, new = {newRank}")
        game.rank = newRank
        game.save()
    serializer = GameSerializer(games, many=True)
    return Response("Hello World")
