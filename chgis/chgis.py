import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("cbdb_addr")

@mcp.tool()
async def search_historical_places(name: str, year: int = None, feature_type: str = None, parent: str = None, start: int = 1, list_length: int = 10) -> dict:
    """
    Searches for historical place names in the TGAZ (Temporal Gazetteer) database.

    Args:
        name (str): The place name to search for. Can be provided in various languages including 
                    Chinese, Pinyin, Tibetan, or Russian.
        year (int, optional): Year of existence filter (valid years for Chinese records: -222 to 1911).
        feature_type (str, optional): Feature type/class of placename (e.g., 'xian', 'zhou', 'cun zhen').
        parent (str, optional): The immediate parent jurisdiction where the place was located.
        start (int): Pagination start index. Defaults to 1.
        list_length (int): Number of results per page. Defaults to 10.

    Returns:
        dict: A dictionary containing:
            - system: Information about the data source system
            - memo: Description of the search query
            - count of displayed results: Number of results shown
            - count of total results: Total number of matching records
            - placenames: List of dictionaries with place information including:
                - sys_id: Unique identifier for the place
                - uri: URI for accessing detailed place information
                - name: Place name
                - transcription: Romanized transcription of the name
                - years: Time period when the place existed
                - parent sys_id: ID of the parent administrative unit
                - parent name: Name of the parent administrative unit
                - feature type: Type of administrative or geographic feature
                - object type: Spatial representation type (POINT or POLYGON)
                - xy coordinates: Geographical coordinates
                - data source: Origin of the data

    Example Usage:
        To search for places named "平江府":
        search_historical_places(name="平江府")
        
        To search for places with "龍" that existed around 800 CE:
        search_historical_places(name="龍", year=800)
        
        To search for "xian" feature types with name containing "庆" in year 1420:
        search_historical_places(name="庆", feature_type="xian", year=1420, parent="Chuzhou")
    """
    api_url = "http://tgaz.fudan.edu.cn/tgaz/placename"
    
    # Build parameters for faceted search
    params = {"fmt": "json", "n": name}
    
    if year is not None:
        params["yr"] = year
    if feature_type is not None:
        params["ftyp"] = feature_type
    if parent is not None:
        params["p"] = parent
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, params=params)
            response.raise_for_status()
            results = response.json()
            
            # Check if we have results and perform client-side pagination if needed
            if "placenames" in results and results["placenames"]:
                placenames = results["placenames"]
                # Apply pagination (client-side)
                paginated_results = placenames[start-1:start-1+list_length] if start <= len(placenames) else []
                
                # Update the response with paginated results
                results["placenames"] = paginated_results
                results["count of displayed results"] = str(len(paginated_results))
                
                # Add pagination info to the response
                results["pagination"] = {
                    "start": start,
                    "end": min(start + len(paginated_results) - 1, len(placenames)) if len(paginated_results) > 0 else start,
                    "total_pages": (len(placenames) + list_length - 1) // list_length
                }
            
            return results
            
    except httpx.RequestError as exc:
        return {"error": f"API request failed: {exc}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}

@mcp.tool()
async def get_place_details(place_id: str) -> dict:
    """
    Retrieves detailed information about a specific historical place by its ID.
    
    Args:
        place_id (str): The unique identifier of the place (e.g., 'hvd_80547')
        
    Returns:
        dict: Detailed information about the historical place including:
            - system: Data source information
            - license: License information for the data
            - uri: URI reference for the place
            - sys_id: Unique identifier for the place
            - spellings: List of different written forms and transcriptions
            - feature_type: Administrative unit type information
            - temporal: Time period information (begin/end years)
            - spatial: Geographic location information
            - historical_context: Information about parent jurisdictions, subordinate units, etc.
            - data source: Origin database of the record
            - source note: Detailed historical notes and citations
        
    Example Usage:
        To get details for place with ID 'hvd_80547' (腾冲府/Tengchong Fu):
        get_place_details(place_id="hvd_80547")
    """
    # The ID should already include the 'hvd_' prefix
    if not place_id.startswith("hvd_"):
        place_id = f"hvd_{place_id}"
        
    api_url = f"http://tgaz.fudan.edu.cn/tgaz/placename/json/{place_id}"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url)
            response.raise_for_status()
            place_data = response.json()
            
            # Handle any potential parsing issues with source_note
            if "source note" in place_data and isinstance(place_data["source note"], str):
                # In some cases, the source note might be an incomplete or malformed JSON string
                # We'll keep it as is, but ensure it doesn't cause issues
                pass
                
            return place_data
            
    except httpx.RequestError as exc:
        return {"error": f"API request failed: {exc}"}
    except httpx.HTTPStatusError as exc:
        return {"error": f"HTTP error status: {exc.response.status_code}"}
    except ValueError as exc:
        # This might happen if the JSON parsing fails
        return {"error": f"Invalid response format: {exc}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')