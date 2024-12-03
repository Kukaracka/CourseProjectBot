async def create_weather_list(weather_term, weather_cond):
    weather_term = weather_term.split(',')
    weather_cond = weather_cond.split(',')
    result = (f"    Ночью - {weather_cond[0]}, {weather_term[0]} °C\n    Утром - {weather_cond[1]}, {weather_term[1]} °C\n"
              f"    Днем - {weather_cond[2]}, {weather_term[2]} °C\n    Вечером - {weather_cond[3]}, {weather_term[3]} °C\n\n")
    return result


async def create_task_list(data):
    data = sorted(data)
    result = ""
    for i, j in enumerate(data):
        if j[0] == "1":
            result += f'    {str(i+1)}. {j[1]} (ежедневно)\n'
        else:
            result += f'    {str(i+1)}. {j[1]} ({j[0]})\n'
    return result