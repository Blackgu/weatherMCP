from mcp.server.fastmcp import FastMCP

from component.wrapper import BASE_URL, make_nws_request, format_alert, format_forecast
from component.city_code import init_city_codes

ACCESS_KEY = '819e27eccea420a48463e6f63f0386b5'
file_path = "./file/AMap_adcode_citycode.xlsx"

divisions = init_city_codes(file_path)

mcp = FastMCP("weather")

def get_citycode(city_name: str) -> str:
    for division_name, division in divisions.items():
        if city_name == division_name:
            return division.adcode
    return None


@mcp.tool()
async def get_alerts(city_name: str) -> str:
    """
    查询输入城市的当天的天气情况
    Args:
        city_name: 城市名称，例如：北京市
    """

    url = f"{BASE_URL}?key={ACCESS_KEY}&city={get_citycode(city_name)}&extensions=base"
    data = await make_nws_request(url)

    if not data or "lives" not in data:
        return "Unable to fetch alerts or no alerts found."

    if not data["lives"]:
        return "No active alerts for this state."

    alerts = [format_alert(live) for live in data["lives"]]
    return "\n---\n".join(alerts)

@mcp.tool()
async def get_forecast(city_name: str) -> str:
    """
    获取输入城市未来三天的天气预报
    Args:
        city_name: 城市名称，例如：北京市
    """
    # First get the forecast grid endpoint
    url = f"{BASE_URL}?key={ACCESS_KEY}&city={get_citycode(city_name)}&extensions=all"
    data = await make_nws_request(url)

    if not data or "forecast" not in data:
        return "Unable to fetch alerts or no alerts found."

    if not data["forecast"]:
        return "No active alerts for this state."

    forecast = format_forecast(data["forecast"])
    return "\n---\n".join(forecast)

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')