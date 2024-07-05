import openai
import re
import matplotlib.pyplot as plt
import numpy as np
from django.shortcuts import render, redirect
from django.http import HttpResponse
from io import BytesIO
from .forms import UserProfileForm, MealRecordForm
from .models import UserProfile, MealRecord

# OpenAI APIキーを設定
openai.api_key = 'Pb64EVUTCQ8GbszYYH2CGLa8seXvErimrP7HrZkhOmo3SFNpixtcp_zJgFK1z4sMyq9jaHwMbTc0jCtO9MIy0Mw'
openai.api_base = 'https://api.openai.iniad.org/api/v1'

def get_nutritional_info(food_name):
    if food_name == "なし":
        return {"カロリー": 0, "タンパク質": 0, "脂質": 0, "炭水化物": 0}

    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[
            {'role': 'user', 'content': f'{food_name}の栄養素とカロリーのみを答えてください。それ以外の情報は載せないでください。'}
        ],
        max_tokens=100,
        temperature=0.5
    )

    nutritional_info = response['choices'][0]['message']['content']
    print(nutritional_info)

    def parse_nutritional_info(info):
        nutrients = {
            "カロリー": 0,
            "タンパク質": 0,
            "脂質": 0,
            "炭水化物": 0
        }
        patterns = {
            "カロリー": r"カロリー.*?(\d+\.?\d*)\s*kcal",
            "タンパク質": r"たんぱく質.*?(\d+\.?\d*)\s*g",
            "脂質": r"脂質.*?(\d+\.?\d*)\s*g",
            "炭水化物": r"炭水化物.*?(\d+\.?\d*)\s*g"
        }
        for key, pattern in patterns.items():
            match = re.search(pattern, info)
            if match:
                nutrients[key] = float(match.group(1))
        return nutrients

    return parse_nutritional_info(nutritional_info)

def register_user(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('top')
    else:
        form = UserProfileForm()
    return render(request, 'register.html', {'form': form})

def record_meal(request, meal_type):
    if request.method == 'POST':
        form = MealRecordForm(request.POST)
        if form.is_valid():
            meal_record = form.save(commit=False)
            meal_record.user = UserProfile.objects.first()  # 簡易のために最初のユーザーを取得
            meal_record.meal_type = meal_type
            food_items = form.cleaned_data['food_items']

            # 食品情報の取得と保存
            nutritional_info = get_nutritional_info(food_items)
            meal_record.calories = nutritional_info["カロリー"]
            meal_record.protein = nutritional_info["タンパク質"]
            meal_record.fat = nutritional_info["脂質"]
            meal_record.carbs = nutritional_info["炭水化物"]

            meal_record.save()
            return redirect('top')
    else:
        form = MealRecordForm()
    return render(request, 'record_meal.html', {'form': form, 'meal_type': meal_type})

def top(request):
    return render(request, 'top.html')

def feedback(request):
    user = UserProfile.objects.first()
    meal_records = MealRecord.objects.filter(user=user)

    nutrients_total = {"カロリー": 0, "タンパク質": 0, "脂質": 0, "炭水化物": 0}
    for record in meal_records:
        nutrients_total["カロリー"] += record.calories
        nutrients_total["タンパク質"] += record.protein
        nutrients_total["脂質"] += record.fat
        nutrients_total["炭水化物"] += record.carbs

    # 基礎代謝量（BMR）の計算
    if user.gender == '男性':
        bmr = 88.36 + (13.4 * user.weight) + (4.8 * user.height) - (5.7 * user.age)
    else:
        bmr = 447.6 + (9.2 * user.weight) + (3.1 * user.height) - (4.3 * user.age)

    # 活動レベルに応じた消費カロリーの計算
    if user.activity_level == '軽度':
        daily_calories = bmr * 1.2
    elif user.activity_level == '中程度':
        daily_calories = bmr * 1.55
    else:
        daily_calories = bmr * 1.725

    # 目標に応じたカロリー調整
    if user.goal == '減量':
        ideal_calories = daily_calories - 500
    elif user.goal == '増量':
        ideal_calories = daily_calories + 500
    else:
        ideal_calories = daily_calories

    # 理想の栄養素の計算
    ideal_protein = user.weight * 1.6  # 体重1kgあたり1.6gのタンパク質
    ideal_fat = ideal_calories * 0.25 / 9  # 総カロリーの25%を脂質から摂取
    ideal_carbs = (ideal_calories - (ideal_protein * 4 + ideal_fat * 9)) / 4  # 残りを炭水化物から摂取

    # 理想の摂取値と実際の摂取値を比較するためのデータを作成
    ideal_values = [ideal_calories, ideal_protein, ideal_fat, ideal_carbs]
    actual_values = [nutrients_total["カロリー"], nutrients_total["タンパク質"], nutrients_total["脂質"], nutrients_total["炭水化物"]]
    labels = ["カロリー", "タンパク質", "脂質", "炭水化物"]

    # グラフをプロット
    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(10, 6))

    bar_width = 0.35
    opacity = 0.8

    rects1 = plt.bar(x, ideal_values, bar_width, alpha=opacity, color='b', label='理想の摂取値')
    rects2 = plt.bar(x + bar_width, actual_values, bar_width, alpha=opacity, color='g', label='実際の摂取値')

    plt.xlabel('栄養素')
    plt.ylabel('摂取量')
    plt.title('理想の摂取値と実際の摂取値の比較')
    plt.xticks(x + bar_width / 2, labels)
    plt.legend()

    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    return HttpResponse(buffer, content_type='image/png')
