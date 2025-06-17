import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("cbdb_addr")

@mcp.tool()
async def search_places_under_location(name: str, accurate: int = 1, startTime: int = None, endTime: int = None, start: int = 1, list_length: int = 10) -> dict:
    """
    Searches for all locations belonging to a specific parent location ID in the CBDB database.

    Retrieves a paginated list of sub-locations for a given parent location ID.

    Args:
        name (str): The location name to search for. Must be provided in English or Chinese.
        accurate (int): Matching mode — 0 for exact match, 1 for fuzzy match. Defaults to 1 (fuzzy).
        startTime (int, optional): Start time filter for location lifespan.
        endTime (int, optional): End time filter for location lifespan.
        start (int): Pagination start index (starting record). Defaults to 1.
        list_length (int): Number of results per page. Defaults to 10.

    Returns:
        dict: A dictionary with keys:
            - total: Total record count
            - start: Starting index of current results
            - end: Ending index of current results
            - data: List of location dictionaries with pId, pName, pNameChn, etc.

    Example Usage:
        To search for locations named "廣州市" (fuzzy match):
        search_location_by_name(name="廣州市", accurate=1)
    """
    api_url = "https://input.cbdb.fas.harvard.edu/api/place_list"
    params = {
        "name": name,
        "accurate": accurate,
        "start": start,
        "list": list_length
    }

    # Include optional filters only if provided
    if startTime is not None:
        params["startTime"] = startTime
    if endTime is not None:
        params["endTime"] = endTime

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, params=params)
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as exc:
        return {"error": f"API request failed: {exc}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}
    
if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')