// keep track of Leaflet map for use between functions
var globalMapObject;

// keep track of which map tiles have been selected
var globalCurrentTilesSelection;
var globalCurrentTiles;

// keep track of items added
var globalFeatureIDTracker = {};

// keep track of statistics and their full names
var globalCurrentStat;
var globalDefaultStat = "STEM_Pct";
var globalStatName = {
	"Tot_P_P": "Total population"
	, "STEM_Pct": "Proportion of qualifications in STEM"
	, "Wkly_Hhd_Inc": "Median weekly household income"
	, "Y12_Comp_Pct": "Year 12 completion rate"
	, "Secondary_Tot_P": "Number of people in secondary education"
	, "Secondary_Pct": "Proportion of people in secondary education"
	, "Tec_Furt_Educ_inst_Tot_P": "Number of people in TAFE education"
	, "TAFE_Pct": "Proportion of people in TAFE education"
	, "Uni_other_Tert_Instit_Tot_P": "Number of people in Uni or other tertiary education"
	, "Uni_Pct": "Proportion of people in Uni or other tertiary education"
	, "Indigenous_Pct": "Proportion of people identifying as Aboriginal/Torres Strait Islander"
}

// Keeping track of CSV data column indices
var totalPopIndex = 2;
var stemPctIndex = 5;
var hhdIncIndex = 6;
var secondaryTotIndex = 7;
var secondaryPctIndex = 8;
var tafeTotIndex = 9;
var tafePctIndex = 10;
var uniTotIndex = 11;
var uniPctIndex = 12;
var y12CompPctIndex = 13;
var indigenousPctIndex = 14;

// Keep track of min/max for different stats for choropleth colouring
var globalMinMaxDictionary = {}

// Colours
var weakEndRGB = {red: 255, green: 0, blue: 0};
var midwayRGB = {red: 255, green: 255, blue: 0};
var strongEndRGB = {red: 0, green: 255, blue: 0};

// Moved here for access by other MapHelper.changeMapStyle()
var mysubset = {
	"type": "FeatureCollection",
	"features": []
}

function bodyDidLoad() {
	ShowtimeHelper.setDarkModeAccordingToBrowser();
	ShowtimeHelper.initialiseSelect2();
	// Set the default statistic to be shown by choropleth
	ShowtimeHelper.setDefaultStat(globalDefaultStat);

	globalMapObject = L.map('mapid').setView([-33.918, 151.23], 7);
	globalCurrentTiles.addTo(globalMapObject);

	$.get("stats-min-max.csv", function(statsMinMaxCSVString) {
		var statsMinMaxArray = Papa.parse(statsMinMaxCSVString);

		// obtain max and min for different stats for colour helper
		for (var i = 1; i < statsMinMaxArray.data.length; i++) {
			var thisStat = statsMinMaxArray.data[i][0];
			var thisMin = parseInt(statsMinMaxArray.data[i][2]);
			var thisMax = parseInt(statsMinMaxArray.data[i][3]);
			globalMinMaxDictionary[thisStat] = [thisMin, thisMax]
		}

		$.get("postcode-stats.csv", function(postcodeStatsCSVString) {
			var postcodeStats = Papa.parse(postcodeStatsCSVString);

			$.get("postcodes-geojson/au-postcodes-Visvalingam-0.1.geojson", function(incomingGeoJSON) {
				var postcodeBoundaries = JSON.parse(incomingGeoJSON);
		
				postcodeBoundaries["features"].forEach(function(item, index) {
					var postcode = "POA" + item["properties"]["POA_CODE16"];

					// set 0
					var csvIndex = 0;

					// find the row containing data for the postcode
					for (var i = 1; i < postcodeStats.data.length; i++) {
						if (postcodeStats.data[i][0] == postcode) {
							csvIndex = i;
						}
					}
					// if the postcode's row has been found, 
					if (csvIndex > 0) {
						// add the different statistics as properties to the postcode
						item["properties"]["STEM_Pct"] = postcodeStats.data[csvIndex][stemPctIndex];
						item["properties"]["Wkly_Hhd_Inc"] = postcodeStats.data[csvIndex][hhdIncIndex];
						item["properties"]["Tot_P_P"] = postcodeStats.data[csvIndex][totalPopIndex];
						item["properties"]["Y12_Comp_Pct"] = postcodeStats.data[csvIndex][y12CompPctIndex];
						item["properties"]["Secondary_Tot_P"] = postcodeStats.data[csvIndex][secondaryTotIndex];
						item["properties"]["Secondary_Pct"] = postcodeStats.data[csvIndex][secondaryPctIndex];
						item["properties"]["Tec_Furt_Educ_inst_Tot_P"] = postcodeStats.data[csvIndex][tafeTotIndex];
						item["properties"]["TAFE_Pct"] = postcodeStats.data[csvIndex][tafePctIndex];
						item["properties"]["Uni_other_Tert_Instit_Tot_P"] = postcodeStats.data[csvIndex][uniTotIndex];
						item["properties"]["Uni_Pct"] = postcodeStats.data[csvIndex][uniPctIndex];
						item["properties"]["Indigenous_Pct"] = postcodeStats.data[csvIndex][indigenousPctIndex];

						// set initial choropleth colouring based on the default statistic
						var thisDefaultStat = item["properties"][globalDefaultStat];
						var thisFeatureDefaultStatRelativePosition = ColourHelper.valueToPercentile(
							globalMinMaxDictionary[globalDefaultStat][0]
							, globalMinMaxDictionary[globalDefaultStat][1]
							, thisDefaultStat
						);
						var thisStyle = {
							"color": ColourHelper.colourGradientHTMLString3(
								weakEndRGB, midwayRGB, strongEndRGB, thisFeatureDefaultStatRelativePosition
							)
						};

						// and push the postcode object to different functions for further handling
						mysubset.features.push(item);
						MapHelper.processAddedPostcode(item, thisStyle);
						NavbarHelper.addItemToSelector(item["properties"]["POA_CODE16"],item["properties"]["POA_NAME16"]);
					}
				});
			});
		});
	});
	
	L.marker([-32.5579652,148.925231]).addTo(globalMapObject).bindPopup('<strong>2820</strong></br>Apsley, Arthurville, Bakers Swamp, Bodangora,</br>'
		+ 'Comobella, Curra Creek, Dripstone, Farnham, Gollan, </br>Lake Burrendong, Maryvale, Medway, Montefiores,</br>'
		+ 'Mookerawa, Mount Aquila, Mount Arthur, Mumbil,</br>Neurea, Spicers Creek, Stuart Town, Suntop,</br>Walmer, Wellington, Wuuluman, Yarragal');

	L.marker([-37.0594311,144.2129333]).addTo(globalMapObject).bindPopup('<strong>3450</strong></br>Castlemaine, Moonlight Flat');

	L.marker([-38.3726257,142.4843849]).addTo(globalMapObject).bindPopup('<strong>3280</strong></br>Dennington, Warrnambool');
}
