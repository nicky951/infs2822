class MapHelper {

	/**
	 * Creates a feature for each postcode
	 * 
	 * @param {Object.<string, string>} item item representation of feature
	 * @param {Object.<string, string>} style A dictionary with `color`, `opacity`, `weight`, `dashArray`, etc.
	 */
	static processAddedPostcode(item, style) {
		var this_id = item["properties"]["POA_CODE16"];
		console.log("this_id = " + this_id);

		var settings = {
			onEachFeature: function(feature, layer) {
				// https://leafletjs.com/examples/geojson/
				var preparedString = "";
				if (feature.properties && feature.properties["POA_CODE16"]) {
                    var preparedString = "<strong>" + feature.properties["POA_CODE16"] + "</strong>";
				}

				if (feature.properties && feature.properties["Tot_P_P"]) {
                    preparedString += "<br />Population: <code>" + parseInt(feature.properties["Tot_P_P"]) + "</pre></code>";
				}

				if (feature.properties && feature.properties["Wkly_Hhd_Inc"]) {
                    preparedString += "<br />Median Weekly Household Income: <code>$" + parseInt(feature.properties["Wkly_Hhd_Inc"]) + "</pre></code>";
				}

				if (feature.properties && feature.properties["STEM_Pct"]) {
                    preparedString += "<br />Proportion of qualifications in STEM: <code>" + parseFloat(feature.properties["STEM_Pct"]).toFixed(2) + "%</pre></code>";
				}

				if (feature.properties && feature.properties["Y12_Comp_Pct"]) {
                    preparedString += "<br />Year 12 completion rate: <code>" + parseFloat(feature.properties["Y12_Comp_Pct"]).toFixed(2) + "%</pre></code>";
				}

				if (feature.properties && (feature.properties["Secondary_Tot_P"] && feature.properties["Secondary_Pct"])) {
					preparedString += "<br />People in secondary education: <code>" + parseInt(feature.properties["Secondary_Tot_P"])
						+ " (" + parseFloat(feature.properties["Secondary_Pct"]).toFixed(2) + "%)</pre></code>";
				}

				if (feature.properties && (feature.properties["Tec_Furt_Educ_inst_Tot_P"] && feature.properties["TAFE_Pct"])) {
					preparedString += "<br />People in TAFE education: <code>" + parseInt(feature.properties["Tec_Furt_Educ_inst_Tot_P"])
						+ " (" + parseFloat(feature.properties["TAFE_Pct"]).toFixed(2) + "%)</pre></code>";
				}

				if (feature.properties && (feature.properties["Uni_other_Tert_Instit_Tot_P"] && feature.properties["Uni_Pct"])) {
					preparedString += "<br />People in uni or other tertiary education: <code>" + parseInt(feature.properties["Uni_other_Tert_Instit_Tot_P"])
						+ " (" + parseFloat(feature.properties["Uni_Pct"]).toFixed(2) + "%)</pre></code>";
				}

				if (feature.properties && feature.properties["Indigenous_Pct"]) {
                    preparedString += "<br />Proportion Indigenous Australian: <code>" + parseFloat(feature.properties["Indigenous_Pct"]).toFixed(2) + "%</pre></code>";
				}

				if (preparedString.length > 0) {
					layer.bindPopup(preparedString);
				}
		
				// // https://stackoverflow.com/questions/14756420/emulate-click-on-leaflet-map-item
				if (feature.properties && feature.properties["ID"]) {
					globalFeatureIDTracker[feature["ID"] + ""] = layer._leaflet_id;
				}
			}
		}

		if (style) {
			settings.style = style;
		}

		var addedFeature = L.geoJSON(item, settings).addTo(globalMapObject);

		globalFeatureIDTracker[this_id] = {
			"leaflet_id": Object.keys(addedFeature["_layers"])[0],
			"captured_geojson_object": addedFeature
		};


	}

	/**
	 * Simulates a mouse click on a place on the map.
	 * 
	 * @param {Object} selectedPlace The logical ID of the place on the map.
	 */
	static simulateMouseClick(selectedPlace) {
		var leafletID = globalFeatureIDTracker[selectedPlace]["leaflet_id"];
		var capturedGeoJSONObject = globalFeatureIDTracker[selectedPlace]["captured_geojson_object"];
		var layer = capturedGeoJSONObject.getLayer(leafletID);
		
		// https://stackoverflow.com/questions/14756420/emulate-click-on-leaflet-map-item
		// fire event 'click' on target layer 
		layer.fireEvent('click');

	}

	/**
	 * Change the colours of each postcode on the choropleth map according to a selected statistic.
	 * 
	 * @param {Object} selectedStat The selected statistic of the map
	 */
	static changeMapStyle(selectedStat) {
		mysubset["features"].forEach(function(element) {
			var feature = globalFeatureIDTracker[element["properties"]["POA_CODE16"]]["captured_geojson_object"];
			feature.setStyle({"color": ColourHelper.colourGradientHTMLString3(
				weakEndRGB, midwayRGB, strongEndRGB, ColourHelper.valueToPercentile(
					globalMinMaxDictionary[selectedStat][0]
					, globalMinMaxDictionary[selectedStat][1]
					, element["properties"][selectedStat]
				)
			)});
		});

	}
}
