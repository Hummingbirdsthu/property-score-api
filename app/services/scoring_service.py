def calculate_score(data: dict):
    area = data.get("area", 0)
    road_width = data.get("road_width", 0)

    score = (area * 0.5) + (road_width * 0.5)

    return score