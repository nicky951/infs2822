class ShowtimeHelper {
	static setDarkModeAccordingToBrowser() {
		// https://stackoverflow.com/questions/50840168/how-to-detect-if-the-os-is-in-dark-mode-in-browsers
		if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
			NavbarHelper.setNavbarDarkMode(true);
			$("#togglefor_CartoDB_DarkMatter").addClass("active");
			globalCurrentTilesSelection = "CartoDB_DarkMatter";
		} else {
			NavbarHelper.setNavbarDarkMode(false);
			$("#togglefor_CartoDB_Positron").addClass("active");
			globalCurrentTilesSelection = "CartoDB_Positron";
		}
		globalCurrentTiles = MapTileHelper.tileLayers[globalCurrentTilesSelection];
	}

	/**
	 * Initialises interface and sets the default statistic 
	 * 
	 * @param {Object} defaultStat The default statistic to be represented by the choropleth.
	 */
	static setDefaultStat(defaultStat) {
		$("#togglefor_" + defaultStat).addClass("active");
		$("#stat_menu_title").text(globalStatName[defaultStat]);
		globalCurrentStat = defaultStat;
	}
		
	static initialiseSelect2() {
		$('#selectPlace').select2({
			theme: 'bootstrap4',
			width: '15rem',
			// https://stackoverflow.com/questions/28762180/how-to-sort-the-select2-jquery-plugin-options-alphabetically/28764371
			sorter: data => data.sort((a, b) => a.text.localeCompare(b.text))
		});
	}

}