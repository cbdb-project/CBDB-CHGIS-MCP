import httpx
import json
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("cbdb_addr_person")

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

@mcp.tool()
async def query_people_by_place(
    people_place: list[int], 
    place_type: list[str], 
    use_date: int = 0,
    date_type: str = None,
    date_start_time: int = None,
    date_end_time: int = None,
    dyn_start: int = None,
    dyn_end: int = None,
    use_xy: int = 0,
    start: int = 1, 
    list_length: int = 50
) -> dict:
    """
    Searches for people associated with specific locations and place types in the CBDB database.

    Args:
        people_place (list[int]): List of location IDs to search for.
        place_type (list[str]): List of place types to filter by. Options include:
            - "individual" (for person's origin/籍贯)
            - "entry" (for entry into service/入仕)
            - "officePosting" (for official positions/职官)
        use_date (int): Whether to use date filtering. 1 for yes, 0 for no. Defaults to 0.
        date_type (str, optional): The type of date to filter by ("dynasty" or "year"). Default is None.
        date_start_time (int, optional): Start year for filtering. Default is None.
        date_end_time (int, optional): End year for filtering. Default is None.
        dyn_start (int, optional): Start dynasty code for filtering. Default is None.
        dyn_end (int, optional): End dynasty code for filtering. Default is None.
        use_xy (int): Whether to include geographic coordinates. 1 for yes, 0 for no. Defaults to 0.
        start (int): Pagination start index. Defaults to 1.
        list_length (int): Number of results per page. Defaults to 10.

    Returns:
        dict: A dictionary with keys:
            - total: Total record count
            - start: Starting index of current results
            - end: Ending index of current results
            - data: List of people dictionaries with PersonID, Name, NameChn, PlaceType, etc.

    Example Usage:
        To search for people associated with locations 2928, 10522, etc., with place types "individual" and "entry":
        query_people_by_place(
            people_place=[2928, 10522, 12553, 13947, 13949], 
            place_type=["individual", "entry", "officePosting"],
            use_date=1,
            date_type="dynasty",
            dyn_start=17, 
            dyn_end=22
        )
    """
    api_url = "https://input.cbdb.fas.harvard.edu/api/query_place"
    
    # Construct the request payload with all parameters, using null for None values
    payload = {
        "peoplePlace": people_place,
        "placeType": place_type,
        "useDate": use_date,
        "dateType": date_type,
        "dateStartTime": date_start_time,
        "dateEndTime": date_end_time,
        "dynStart": dyn_start,
        "dynEnd": dyn_end,
        "useXy": use_xy,
        "start": start,
        "list": list_length
    }
    
    # Convert the payload to a JSON string for the RequestPayload parameter
    request_payload = json.dumps(payload)
    
    try:
        async with httpx.AsyncClient() as client:
            # Use the GET method with the RequestPayload as a query parameter
            response = await client.get(f"{api_url}?RequestPayload={request_payload}")
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as exc:
        return {"error": f"API request failed: {exc}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')