var mapLoadTime = 1000;

// Unity messaging guard to avoid SendMessage before engine is ready
var unityReady = false;
var unityQueue = [];

document.addEventListener('UnityLoaded', function(){
	unityReady = true;
	if (unityQueue.length > 0 && typeof gameInstance !== 'undefined' && gameInstance) {
		unityQueue.forEach(function(fn){ try { fn(); } catch (e) { console.warn('Unity send queued error', e); } });
		unityQueue = [];
	}
});

function sendToUnity(target, method, payload){
	var action = function(){ gameInstance.SendMessage(target, method, payload || ""); };
	if (unityReady && typeof gameInstance !== 'undefined' && gameInstance) {
		action();
	} else {
		unityQueue.push(action);
	}
}

// State coordinates mapping for Indian states
var stateCoordinates = {
    'Andhra Pradesh': {lat: 15.9129, lon: 79.7400},
    'Arunachal Pradesh': {lat: 28.2180, lon: 94.7278},
    'Assam': {lat: 26.2006, lon: 92.9376},
    'Bihar': {lat: 25.0961, lon: 85.3131},
    'Chhattisgarh': {lat: 21.2787, lon: 81.8661},
    'Goa': {lat: 15.2993, lon: 74.1240},
    'Gujarat': {lat: 23.0225, lon: 72.5714},
    'Haryana': {lat: 29.0588, lon: 76.0856},
    'Himachal Pradesh': {lat: 31.1048, lon: 77.1734},
    'Jharkhand': {lat: 23.6102, lon: 85.2799},
    'Karnataka': {lat: 15.3173, lon: 75.7139},
    'Kerala': {lat: 10.8505, lon: 76.2711},
    'Madhya Pradesh': {lat: 22.9734, lon: 78.6569},
    'Maharashtra': {lat: 19.7515, lon: 75.7139},
    'Manipur': {lat: 24.6637, lon: 93.9063},
    'Meghalaya': {lat: 25.4670, lon: 91.3662},
    'Mizoram': {lat: 23.1645, lon: 92.9376},
    'Nagaland': {lat: 26.1584, lon: 94.5624},
    'Odisha': {lat: 20.9517, lon: 85.0985},
    'Punjab': {lat: 31.1471, lon: 75.3412},
    'Rajasthan': {lat: 27.0238, lon: 74.2179},
    'Sikkim': {lat: 27.5330, lon: 88.5122},
    'Tamil Nadu': {lat: 11.1271, lon: 78.6569},
    'Telangana': {lat: 18.1124, lon: 79.0193},
    'Tripura': {lat: 23.9408, lon: 91.9882},
    'Uttar Pradesh': {lat: 26.8467, lon: 80.9462},
    'Uttarakhand': {lat: 30.0668, lon: 79.0193},
    'West Bengal': {lat: 22.9868, lon: 87.8550}
};

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
	sendToUnity("CitySimulatorMap", "jsSetMap", paramsJSON);
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
	sendToUnity("CitySimulatorMap", "jsSetMap", paramsJSON);
}


function extendMap(west, east, north, south){
	mapParams = {"west": west, "east":east, "north":north, "south":south};
	var paramsJSON = JSON.stringify(mapParams);
	sendToUnity("CitySimulatorMap", "jsSetExtent", paramsJSON);
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
	sendToUnity("CitySimulatorMap", "jsSetPOIs", paramsJSON);	
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
								{"lat": 19.0640,
									"lon": 72.8350,
									"type": "RainGauge", 
									"height": 75,
									"content": "IMD Rain Gauge\nLast Reading: 25 mm/hr\nMonsoon Alert: Active"},
								{"lat": 19.0550, 
									"lon": 72.8380,
									"type": "Soil", 
									"height": 65,
									"content": "Hydro Station\nGroundwater: Normal\nSoil Moisture: 45%\nWind: 15 km/h from SW"},
		
			]};

	var buildingPOIs = {"pois": [
								{"lat": 19.0540, 
									"lon": 72.8230, 
									"type": "Damage", 
									"height": 75,
									"content": "Damage Estimate\nCommercial Building\nStructure Damage: ₹2.5L\nContent Damage: ₹8.2L"},
								{"lat": 19.0620,
									"lon": 72.8360, 
									"type": "Damage", 
									"height": 85,
									"content": "Damage Estimate\nResidential Complex\nStructure Damage: 12%\nContent Damage: 28%"},
		
			]};

	var warningPOIs = {"pois": [
								{"lat": 19.0600,
									"lon": 72.8300,
									"type": "Warning",
									"height": 100,
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
	sendToUnity("CitySimulatorMap", "jsEnableTraffic", "all");	
}

function generateFlood(){
	sendToUnity("CitySimulatorMap", "jsGenerateFlood", "");	
}

function generateFire(poiJSON){
	var paramsJSON = JSON.stringify(poiJSON);
	sendToUnity("CitySimulatorMap", "jsSetFire", paramsJSON);	
}

function adjustFlood(level){
	mapParams = {"floodLevel": level};
	var paramsJSON = JSON.stringify(mapParams);
	sendToUnity("CitySimulatorMap", "jsAdjustFlood", paramsJSON);
}

function setUserName(){
	sendToUnity("CameraMain", "jsSetProfile", "India User");	
}

// Dynamic VR initialization based on URL parameters (from prediction dashboard)
function initializePredictionBasedVR() {
	const urlParams = new URLSearchParams(window.location.search);
	const state = urlParams.get('state');
	const hazard = urlParams.get('hazard');
	const probability = parseFloat(urlParams.get('probability'));
	
	if (state && hazard && probability) {
		console.log(`Loading VR for ${state} - ${hazard} (Risk: ${(probability * 100).toFixed(1)}%)`);
		
		// Get state coordinates
		const coords = stateCoordinates[state];
		if (!coords) {
			console.warn(`Coordinates not found for state: ${state}`);
			return;
		}
		
		// Calculate disaster extent based on probability
		const floodLevel = probability * 5; // 0-5 meter range
		const fireIntensity = Math.floor(probability * 10); // 0-10 scale
		
		// Update map to state location
		updateMapLocation(coords.lat, coords.lon, 13);
		
		setTimeout(function(){
			if (hazard === 'flood') {
				// Generate flood scenario
				generateFlood();
				setTimeout(function(){
					adjustFlood(floodLevel);
					
					// Add custom POI for this state
					var customPOI = {"pois": [{
						"lat": coords.lat,
						"lon": coords.lon,
						"type": "Warning",
						"height": 80,
						"content": `${state} Flood Alert\nRisk Level: ${(probability * 100).toFixed(1)}%\nWater Level: ${floodLevel.toFixed(1)}m\nSource: ML Prediction`
					}]};
					addPOI(customPOI);
				}, 500);
			} else if (hazard === 'fire') {
				// Generate fire scenario with scaled intensity
				var firePOIs = {"pois": []};
				
				// Create multiple fire points based on intensity
				for (let i = 0; i < fireIntensity; i++) {
					const offsetLat = coords.lat + (Math.random() - 0.5) * 0.02;
					const offsetLon = coords.lon + (Math.random() - 0.5) * 0.02;
					firePOIs.pois.push({
						"lat": offsetLat,
						"lon": offsetLon,
						"type": "Fire"
					});
				}
				
				generateFire(firePOIs);
				
				// Add custom POI for this state
				var customPOI = {"pois": [{
					"lat": coords.lat,
					"lon": coords.lon,
					"type": "Warning",
					"height": 80,
					"content": `${state} Fire Alert\nRisk Level: ${(probability * 100).toFixed(1)}%\nFire Spread: ${fireIntensity}/10\nSource: ML Prediction`
				}]};
				addPOI(customPOI);
			}
			
			enableTraffic();
		}, mapLoadTime);
		
		// Update page title
		document.title = `${state} ${hazard.charAt(0).toUpperCase() + hazard.slice(1)} - GeospatialVR`;
	}
}

// Check if page loaded with prediction parameters
window.addEventListener('load', function() {
	const urlParams = new URLSearchParams(window.location.search);
	const state = urlParams.get('state');
	const hazard = urlParams.get('hazard');
	const probability = parseFloat(urlParams.get('probability'));
	
	if (state && hazard && probability) {
		// Show prediction info panel
		const infoPanel = document.getElementById('prediction-info');
		const detailsElement = document.getElementById('prediction-details');
		if (infoPanel && detailsElement) {
			infoPanel.style.display = 'block';
			detailsElement.innerHTML = `
				<strong>State:</strong> ${state}<br>
				<strong>Hazard:</strong> ${hazard.charAt(0).toUpperCase() + hazard.slice(1)}<br>
				<strong>Risk Probability:</strong> ${(probability * 100).toFixed(1)}%
			`;
		}
		
		// Wait for Unity to load before initializing VR
		if (typeof gameInstance !== 'undefined' && gameInstance) {
			initializePredictionBasedVR();
		} else {
			// Wait for Unity to be ready
			document.addEventListener('UnityLoaded', function() {
				initializePredictionBasedVR();
			});
		}
	}
});