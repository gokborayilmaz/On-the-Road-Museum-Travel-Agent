from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from upsonic import UpsonicClient, Task, AgentConfiguration, ObjectResponse
import os

# Initialize the Upsonic client
client = UpsonicClient("localserver")
client.set_config("AZURE_OPENAI_ENDPOINT", os.getenv("AZURE_OPENAI_ENDPOINT"))
client.set_config("AZURE_OPENAI_API_VERSION", os.getenv("AZURE_OPENAI_API_VERSION"))
client.set_config("AZURE_OPENAI_API_KEY", os.getenv("AZURE_OPENAI_API_KEY"))

client.default_llm_model = "azure/gpt-4o"

# Define Google Maps MCP
@client.mcp()
class GoogleMapsMCP:
    command = "npx"
    args = [
        "-y",
        "@modelcontextprotocol/server-google-maps"
    ]
    env = {
        "GOOGLE_MAPS_API_KEY": os.getenv("GOOGLE_MAPS_API_KEY")
    }

# Define the FastAPI app
app = FastAPI()

# Input model for travel plan
class TravelInput(BaseModel):
    origin: str
    destination: str

# Define response formats
class RouteWithMuseumsResponse(ObjectResponse):
    cities: list[str]  # Cities along the route
    distance: str
    duration: str
    total_museums: int

class Musium(ObjectResponse):
    name_of_musium: str
    location: str
    paid: bool
    open_time: str

class MuseumsPerCityResponse(ObjectResponse):
    city_museums: list[Musium]  # List of cities with their respective museums

@app.post("/find-route-and-museums/")
async def find_route_and_museums(input_data: TravelInput):
    # Define the agent configuration
    travel_agent = AgentConfiguration(
        job_title="Travel Planner",
        company_url="https://upsonic.ai",
        company_objective="Find the most efficient and informative travel routes.",
        reflection=True
    )

    # Step 1: Find the best route with the most museums
    route_task = Task(
        description=(
            f"Find the best route between {input_data.origin} and {input_data.destination} with the most museums, "
            "but without making the road significantly longer. Include cities along the route, total distance, "
            "duration, and the total number of museums."
        ),
        tools=[GoogleMapsMCP],
        response_format=RouteWithMuseumsResponse
    )

    client.agent(travel_agent, route_task)
    route_data = route_task.response
    if not route_data:
        raise HTTPException(status_code=500, detail="Failed to find the best route.")

    # Step 2: List museums for each city along the route
    cities = ", ".join(route_data.cities)
    museums_task = Task(
        description=(
            f"List all museums for the cities along the route: {cities}."
            "Provide details including the city name and museum information."
        ),
        tools=[GoogleMapsMCP],
        response_format=MuseumsPerCityResponse,
        context=[route_task]
    )

    client.agent(travel_agent, museums_task)
    museums_data = museums_task.response
    if not museums_data:
        raise HTTPException(status_code=500, detail="Failed to list museums for the cities.")

    # Return the combined results
    return {
        "route": {
            "cities": route_data.cities,
            "distance": route_data.distance,
            "duration": route_data.duration,
            "total_museums": route_data.total_museums,
        },
        "city_museums": museums_data.city_museums
    }

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Travel Planner</title>
    <style>
        /* Genel Sayfa Stili */
        body {
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 0;
            background: #f9f9f9;
            color: #333;
        }

        header {
            background: #007BFF;
            color: white;
            padding: 15px 20px;
            text-align: center;
            box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.2);
        }

        h1 {
            margin: 0;
        }

        .container {
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
            background: white;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
        }

        form {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        label {
            font-weight: bold;
        }

        input, button, textarea {
            font-size: 16px;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            width: 100%;
        }

        button {
            background: #007BFF;
            color: white;
            font-weight: bold;
            border: none;
            cursor: pointer;
            transition: background 0.3s ease;
        }

        button:hover {
            background: #0056b3;
        }

        #results {
            margin-top: 20px;
            padding: 15px;
            background: #f4f4f4;
            border-radius: 8px;
            white-space: pre-wrap;
            word-wrap: break-word;
        }

        footer {
            text-align: center;
            margin-top: 30px;
            font-size: 0.9em;
            color: #555;
        }

        footer a {
            color: #007BFF;
            text-decoration: none;
        }

        footer a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>

<header>
    <h1>Travel Planner</h1>
</header>

<div class="container">
    <form id="travel-form">
        <label for="origin">🗺️ Origin City:</label>
        <input type="text" id="origin" name="origin" placeholder="Enter your starting city" required>

        <label for="destination">📍 Destination City:</label>
        <input type="text" id="destination" name="destination" placeholder="Enter your destination city" required>

        <button type="button" onclick="submitForm()">Generate Travel Plan</button>
    </form>

    <div id="results" style="display: none;">
        <h2>Results:</h2>
        <pre id="results-content"></pre>
    </div>
</div>

<footer>
    Powered by <a href="https://upsonic.ai" target="_blank">UpsonicAI</a> | © 2025
</footer>

<script>
    async function submitForm() {
        const origin = document.getElementById('origin').value;
        const destination = document.getElementById('destination').value;

        // Gönderim sırasında düğmeyi devre dışı bırak
        const button = document.querySelector('button');
        button.disabled = true;
        button.textContent = 'Generating...';

        try {
            const response = await fetch('/find-route-and-museums/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ origin, destination })
            });

            if (response.ok) {
                const data = await response.json();
                document.getElementById('results').style.display = 'block';
                document.getElementById('results-content').textContent = JSON.stringify(data, null, 2);
            } else {
                document.getElementById('results').style.display = 'block';
                document.getElementById('results-content').textContent = 'Error: Could not generate travel plan.';
            }
        } catch (error) {
            document.getElementById('results').style.display = 'block';
            document.getElementById('results-content').textContent = 'Error: Something went wrong.';
        }

        // Düğmeyi tekrar etkinleştir
        button.disabled = false;
        button.textContent = 'Generate Travel Plan';
    }
</script>

</body>
</html>

    """
