<p align="center"><img alt="GeospatialVR" title="GeospatialVR" src="images/logo.png" width="250"></p>

<h3 align="center">
  A Web-based Virtual Reality Framework for Collaborative Environmental Simulations
</h3>

<br>

## Table of Contents

- [Introduction](#introduction)
- [How To Use](#how-to-use)
- [Use Cases](#use-cases)
  - [Flood - Mumbai](#flood---mumbai-india)
  - [Forest Fire - Uttarakhand](#forest-fire---uttarakhand-india)
- [Feedback](#feedback)
- [To-Do](#to-do)
- [License](#license)
- [Acknowledgements & Citation](#acknowledgements--citation)

## Introduction

This project introduces GeospatialVR, an open-source collaborative virtual reality framework to dynamically create 3D real-world environments that can be served on any web platform and accessed via desktop and mobile devices and virtual reality headsets. The framework can generate realistic simulations of desired locations entailing the terrain, elevation model, infrastructures, dynamic visualizations (e.g. water and fire simulation), and information layers (e.g. disaster damages and extent, sensor readings, occupancy, traffic, weather). These layers enable in-situ visualization of useful data to aid public, scientists, officials, and decision-makers in acquiring a bird's eye view of the current, historical, or forecasted condition of a community. The framework incorporates multiuser support for remote virtual collaboration. GeospatialVR's purpose is to augment cyberinfrastructures with geospatial components to constitute the next-generation of information systems and decision support systems powered by immersive technologies. 

This India-specific implementation focuses on flood and forest fire disaster management scenarios, with case studies developed for flooding in Mumbai and forest fires in Uttarakhand.

![Arch](images/arch.png)

## How To Use

This repository provides a boilerplate to use GeospatialVR. Simply download and run the "index.html".

To examine how the data is provided and visualizations are managed for the VR environment, check out [geospatialxr.js](script/geospatialxr.js)

As a brief summary of basic functionality:

- Load location on the map
```js
updateMapLocation(lat, lon, zoom); // default zoom is 16
```

Extend current map by loading more tiles
```js
extendMap(west, east, north, south); // for initial map, 1 tile is loaded per each direction
```

Enable traffic layer on active map
```js
enableTraffic();
```

Add points of interest with labels on the map
```js
var pois = {"pois": [
                {"lat": 19.0596, 
                  "lon": 72.8295, 
                  "type": "StreamSensor", 
                  "height": 85,
                  "content": "Mithi River Gauge\nHeight: 2.5 m\nDischarge: 450 m³/s"},
                {"lat": 19.0610, 
                  "lon": 72.8310, 
                  "type": "RainGauge", 
                  "height": 70,
                  "content": "IMD Rain Gauge\nLast Reading: 25 mm/hr\nMonsoon Alert: Active"},
      ]};
addPOI(pois);

// Type parameter refers to the label styling. Currently available label types:
// Warning, SensorGeneric, StreamSensor, RainGauge, Soil, Damage, Fireman, FireData
```

Add fire animation to given location(s)
```js
var firePOIs = {"pois": [
                {"lat": 30.3165,
                  "lon": 79.0193,
                  "height": 0},
      ]};
generateFire(firePOIs);
```

## Use Cases

### Flood - Mumbai, India

A case study for flood management in Mumbai, India, showing a flood animation and relevant data layers (i.e. Mithi River gauges, IMD rain gauges, hydro stations for groundwater and soil moisture data, estimated flood damages in Indian Rupees (₹) for current or forecasted flood scenarios, and traffic congestion). Mumbai is prone to monsoon flooding, particularly in the Mithi River area.

Flooding Use Case - Mumbai
:-------------------------:
![Screenshot 1](images/flood.png)

### Forest Fire - Uttarakhand, India

A case study for forest fire management in Uttarakhand, India, showing a fire animation and relevant data layers (i.e. characteristics and center of the forest fire, evacuation requirements for nearby villages, air quality and PM2.5 measurements in the area, forest officer vitals, and traffic congestion). Uttarakhand's Himalayan forests are prone to fires during dry seasons.

Forest Fire Use Case - Uttarakhand
:-------------------------:
![Screenshot 1](images/fire.png)


## Feedback

Feel free to send us feedback by filing an issue.

## To-Do

This framework is currently a functioning prototype, and is not suitable for use at an operational level. 

- Allow users to create rooms for multiuser.
- Race condition exists when multiple users interact at the same environment.
- Always initialize the map at the same location in the virtual room regardless of the location's elevation.
- Allow developers to create custom POI labels by providing color, icon, and font through JS.
- and more...

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements & Citation

This project is developed by the University of Iowa Hydroinformatics Lab (UIHI Lab): [https://hydroinformatics.uiowa.edu/](https://hydroinformatics.uiowa.edu/).

This project utilizes Mapbox Unity SDK and Mozilla Unity WebXR Exporter.

> Sermet, Y. and Demir, I., 2021. GeospatialVR: A web-based virtual reality framework for collaborative environmental simulations. Computers & Geosciences, p.105010. https://doi.org/10.1016/j.cageo.2021.105010

> Sermet, Y. and Demir, I., 2020, November. An Immersive Decision Support System for Disaster Response. In 26th ACM Symposium on Virtual Reality Software and Technology (pp. 1-3). https://doi.org/10.1145/3385956.3422087
