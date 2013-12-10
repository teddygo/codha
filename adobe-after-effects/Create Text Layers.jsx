{
	// slapTextnImage.jsx
	// 
	// This script adds the content within the active comp.
	//

	function zzz(thisObj)
	{
 		var scriptName = "Create Text Layers";
		function yyy()
		{
			var activeItem = app.project.activeItem;
			var myNewSource = "D:\\temp\\facebook.png";
			app.beginUndoGroup(scriptName);
			var myFile = File(myNewSource);
			if (myFile) {
				var myImportOptions = new ImportOptions(myFile);
				//myImportOptions.file = myFile;
				var myFootage = app.project.importFile(myImportOptions);
				alert(activeItem);
				if ((activeItem == null) || !(activeItem instanceof CompItem)) {
					alert("Please select or open a composition first.", scriptName);
				} else {
					var myLayers = activeItem.selectedLayers;
					var layerName = myLayers[0].name;
					alert(layerName);
					var imageLayer = activeItem.layers.add(myFootage);
					var myTransform = imageLayer.Effects.addProperty("Transform");
					myTransform.property(2).setValue([900,520]);
					
			}
		}
		}

		// 
		// The main script.
		//
		if (parseFloat(app.version) < 8) {
			alert("This script requires After Effects CS3 or later.", scriptName);
			return;
		}
		yyy();
	} 
	zzz(this);
}
