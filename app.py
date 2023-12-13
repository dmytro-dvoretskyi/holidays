import json
from openai import OpenAI
import requests
import streamlit as st

def get_holidays(api_key, country="CY", year="2022"):
   
    url = "https://holidayapi.com/v1/holidays"
    params = {
        "country": country,
        "year": year,
        "pretty": "",
        "key": api_key
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return [holiday for holiday in data['holidays'] if holiday['date'].startswith(f'{year}-12')]
    except requests.RequestException as e:
        print(f"Error fetching holidays: {e}")
        return []

def create_prompt(holidays, ideas):
    holiday_details = "\n".join([f"Name: {holiday['name']}\nDate: {holiday['date']}" for holiday in holidays])
    instructions = """
        Ви - аналітик, який допомагає розробляти контент-стратегію для соціальних медіа, зосереджуючись на святкових темах. Ось список грудневих свят та список ідей для постів. Ваша задача - вибрати найбільш відповідні ідеї для кожного свята, враховуючи його значення та актуальність. Поясніть свій вибір.

        Грудневі свята:
        {holiday_details}

        Доступні ідеї:
        {ideas}

        Виберіть та поясніть вибір ідей для кожного з грудневих свят.
        """  # Ваші інструкції
    return instructions.format(holiday_details=holiday_details, ideas=json.dumps(ideas, ensure_ascii=False, indent=2))

def call_openai_gpt(prompt, api_key):
    client = OpenAI(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": "Select and explain the ideas."}
            ],
            max_tokens=1500,
            temperature=0.5
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error in GPT-4 idea selection: {e}")
        return ""

def main(ideas_file_path, openai_api_key, holiday_api_key):
    holidays = get_holidays(holiday_api_key)
    with open(ideas_file_path, 'r', encoding='utf-8') as file:
        ideas = json.load(file)

    prompt = create_prompt(holidays, ideas)
    selected_ideas = call_openai_gpt(prompt, openai_api_key)

    print("Грудневі свята:")
    for holiday in holidays:
        print(f"{holiday['name']} ({holiday['date']})")

    print("Обрані GPT ідеї із поясненням:")
    print(selected_ideas)

# Виклик функції з необхідними параметрами
main('./new_year.json', st.secrets["OPENAI"], st.secrets["HOLIDAYS"])
