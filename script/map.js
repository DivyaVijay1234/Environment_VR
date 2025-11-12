var map;

var currentLocation = {
	address: "Mumbai, Maharashtra",
	postalcode: "400001",
	county: "Mumbai"
};

function initializeMap(){
	console.log('initializing map');
	// Default to Mumbai, India - Mithi River area
	var mapOptions = {
		center: new google.maps.LatLng(19.0596, 72.8295),
		zoom: 16,
		mapTypeId: google.maps.MapTypeId.TERRAIN,
		disableDefaultUI: false,
	};
	map = new google.maps.Map(document.getElementById("map-canvas"), mapOptions);


	google.maps.event.addListener(map, 'click', function( event ){
		loadLocationXR(event.latLng.lat(), event.latLng.lng());
	});
}

// Changes the current location for XR model
function loadLocationXR(lat, lon){
	updateMapLocation(lat, lon);
}


//  HELPER FUNCTIONS

function hideByID(id){
	document.getElementById(id).style.display = "none";
}

function showByID(id){
	document.getElementById(id).style.display = "block";
}

function getAddressComponent(place, componentId){
    for (var i = 0; i < place.address_components.length; i++) {
      for (var j = 0; j < place.address_components[i].types.length; j++) {
        if (place.address_components[i].types[j] == componentId) {
          return place.address_components[i].long_name;
        }
      }
    }
    return 0;
}
