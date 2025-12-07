var mapLoadTime = 1000;

document.getElementById("resizeButton").addEventListener("click", function(){
  var xrcontainer = document.getElementById("xrcontainer");
  xrcontainer.classList.toggle("fullscreen");
  xrcontainer.classList.toggle("smallscreen");
});

// Global variable to track current map parameters
var mapParams = {"lat": 19.0596, "lon": 72.8295, "zoom": 14};

function updateMapLocation(lat, lon, zoom=14){
	mapParams = {"lat": lat, "lon": lon, "zoom": zoom};
	var paramsJSON = JSON.stringify(mapParams);
	gameInstance.SendMessage("CitySimulatorMap", "jsSetMap", paramsJSON);
}

// Function to zoom out for better fullscreen view
function zoomOutView(zoomLevel=12){
	// Use current map location, just change zoom level
	if (mapParams && mapParams.lat && mapParams.lon) {
		mapParams.zoom = zoomLevel;
	} else {
		// Default to Mumbai if no location set
		mapParams = {"lat": 19.0596, "lon": 72.8295, "zoom": zoomLevel};
	}
	var paramsJSON = JSON.stringify(mapParams);
	gameInstance.SendMessage("CitySimulatorMap", "jsSetMap", paramsJSON);
}


function extendMap(west, east, north, south){
	mapParams = {"west": west, "east":east, "north":north, "south":south};
	var paramsJSON = JSON.stringify(mapParams);
	gameInstance.SendMessage("CitySimulatorMap", "jsSetExtent", paramsJSON);
}


// Indian flood sensor POIs - Mumbai example
var streamSensorPOIs = {"pois": [
							{"lat": 19.0596, 
								"lon": 72.8295, 
								"type": "StreamSensor", 
								"content": "Mithi River Gauge \nDepth: 2.5 m"},
							{"lat": 19.0610, 
								"lon": 72.8310, 
								"type": "RainGauge", 
								"content": "IMD Rain Gauge \nStage: 25 mm/hr"},
							{"lat": 19.0605, 
								"lon": 72.8300, 
								"type": "Warning", 
								"content": "Flood Warning \nWater Level: 1.8 m"},
	
		]};

function addPOI(pois){
	var paramsJSON = JSON.stringify(pois);
	gameInstance.SendMessage("CitySimulatorMap", "jsSetPOIs", paramsJSON);	
}

// Removed: Transportation use case (Richmond, VA) - Not relevant for India-specific project
// Removed: Active Shooter use case (Richmond, VA) - Not relevant for India-specific project
// Focus: Floods and Forest Fires in India only

function useCaseFloodDouble(){
	useCaseFlood();
	useCaseFlood();
}

function useCaseFlood(){
	// Mumbai, India - Mithi River area (flood-prone)
	// Using zoom level 14 for better overview (was 16, too zoomed in)
	updateMapLocation(19.0596, 72.8295, 14);
	
	extendMap(1, 1, 1, 1);

	// Indian flood monitoring sensors - spaced out to avoid overlapping
	var stageSensorPOIs = {"pois": [
								{"lat": 19.0580,
									"lon": 72.8270,
									"type": "StreamSensor",
									"height": 85,
									"content": "Mithi River Gauge\nHeight: 2.5 m\nDischarge: 450 m³/s\nReported: Current"},
			]};

	var variousSensorsPOIs = {"pois": [
								{"lat": 19.0620,
									"lon": 72.8320,
									"type": "RainGauge", 
									"height": 70,
									"content": "IMD Rain Gauge\nLast Reading: 25 mm/hr\nMonsoon Alert: Active"},
								{"lat": 19.0640, 
									"lon": 72.8340,
									"type": "Soil", 
									"height": 70,
									"content": "Hydro Station\nGroundwater: Normal\nSoil Moisture: 45%\nWind: 15 km/h from SW"},
		
			]};

	var buildingPOIs = {"pois": [
								{"lat": 19.0560, 
									"lon": 72.8250, 
									"type": "Damage", 
									"height": 70,
									"content": "Damage Estimate\nCommercial Building\nStructure Damage: ₹2.5L\nContent Damage: ₹8.2L"},
								{"lat": 19.0600,
									"lon": 72.8290, 
									"type": "Damage", 
									"height": 80,
									"content": "Damage Estimate\nResidential Complex\nStructure Damage: 12%\nContent Damage: 28%"},
		
			]};

	var warningPOIs = {"pois": [
								{"lat": 19.0615,
									"lon": 72.8315,
									"type": "Warning",
									"height": 60,
									"content": "Flood Warning\nWater Level: 1.8 m\nEvacuation Recommended"},
			]};

	addPOI(stageSensorPOIs);
	addPOI(variousSensorsPOIs);
	addPOI(buildingPOIs);
	addPOI(warningPOIs);

	setTimeout(function(){
		generateFlood();
		adjustFlood(0.8); // Adjusted for Indian flood levels
		gameInstance.SendMessage("CitySimulatorMap", "jsSetLayerInactive", "Water");
		enableTraffic();
	}, mapLoadTime);
}

function useCaseFireDouble(){
	useCaseFire();
	useCaseFire();
}

function useCaseFire(){
	// Indian forest fire location - Using a flatter forest area to ensure fire appears on ground
	// Using a location in Maharashtra forest area (flatter terrain) instead of high-altitude Uttarakhand
	// Using zoom level 14 for better overview (was 16, too zoomed in)
	updateMapLocation(19.0760, 73.8777, 14); // Maharashtra forest area (near Mumbai, flatter terrain)

	// Fire POI - height set to 0 to ensure it burns on ground/terrain surface
	// Using flatter terrain location to prevent fire from appearing in sky
	var firePOIs = {"pois": [
								{"lat": 19.0760,
									"lon": 73.8777,
									"type": "N/A",
									"height": 0,
									"content": ""},
			]};

	var fireDataPOIs = {"pois": [
								{"lat": 19.0760,
									"lon": 73.8777,
									"type": "FireData",
									"height": 50,
									"content": "Forest Fire - Maharashtra\nCause: Dry Weather\nFuels: Mixed Forest\nArea Affected: 15 hectares"},
			]};

	var smokePOIs = {"pois": [
								{"lat": 19.0780, 
									"lon": 73.8800,
									"type": "SensorGeneric",
									"height": 50,
									"content": "Air Quality Sensor\nO2: 19.2%\nCO: 28.5 ppm\nPM2.5: 185 μg/m³\nVisibility: 2 km"},
			]};

	var spottedPeoplePOIs = {"pois": [
								{"lat": 19.0740, 
									"lon": 73.8750,
									"type": "SensorGeneric",
									"height": 60,
									"content": "Evacuation Required\nVillage: 3 km away\nPeople at Risk: 120"},
			]};

	var firemanPOIs = {"pois": [
								{"lat": 19.0720, 
									"lon": 73.8730, 
									"type": "Fireman", 
									"height": 45,
									"content": "Forest Officer Rajesh Kumar\nPulse: 112 bpm\nSpO2: 96.2%\nTeam: 8 personnel"},
								{"lat": 19.0770, 
									"lon": 73.8780, 
									"type": "Fireman", 
									"height": 55,
									"content": "Fire Chief Priya Sharma\nPulse: 105 bpm\nSpO2: 96.5%\nCoordination: Active"},
			]};

	// Delay fire generation to ensure terrain is fully loaded before placing fire on ground
	setTimeout(function(){
		// First add POIs
		addPOI(fireDataPOIs);
		addPOI(smokePOIs);
		addPOI(firemanPOIs);
		addPOI(spottedPeoplePOIs);
		// Then generate fire on ground surface after a small additional delay
		setTimeout(function(){
			generateFire(firePOIs);
		}, 500);
		enableTraffic();
	}, mapLoadTime);
}

function enableTraffic(){
	gameInstance.SendMessage("CitySimulatorMap", "jsEnableTraffic", "all");	
}

function generateFlood(){
	gameInstance.SendMessage("CitySimulatorMap", "jsGenerateFlood", "");	
}

function generateFire(poiJSON){
	var paramsJSON = JSON.stringify(poiJSON);
	gameInstance.SendMessage("CitySimulatorMap", "jsSetFire", paramsJSON);	
}

function adjustFlood(level){
	mapParams = {"floodLevel": level};
	var paramsJSON = JSON.stringify(mapParams);
	gameInstance.SendMessage("CitySimulatorMap", "jsAdjustFlood", paramsJSON);
}

function setUserName(){
	gameInstance.SendMessage("CameraMain", "jsSetProfile", "India User");	
}