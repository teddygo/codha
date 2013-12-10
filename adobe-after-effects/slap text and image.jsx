{
	// slapTextnImage.jsx
	// 
	// This script adds the content within the active comp.
	//

	function CreateTextLayers(thisObj)
	{
		var scriptName = "Create Text Layers";
		var value = "";
		var myText = "";

		function fileTextLayer()
		{
			var activeItem = app.project.activeItem;

			if ((activeItem == null) || !(activeItem instanceof CompItem)) {
				alert("Please select or open a composition first.", scriptName);
				} else {

					// By bracketing the operations with begin/end undo group, we can 
					// undo the whole script with one undo operation.
					app.beginUndoGroup(scriptName);
					// Create a text layer.

					var myLayers = activeItem.selectedLayers;
					if(myLayers[0] != null && myLayers[0] != "undefined")
					{
						var layerName = myLayers[0].name;
						layerName = layerName.split(".")
						myText = activeItem.layers.addText(layerName[0]);
						myText.position.setValue( [ 200, 200 ] );
						myText.scale.setValue( [ 200, 200 ] );
						alert(layerName[0]);
					}
					else
					{
						alert("no layer selected");
					}
					app.endUndoGroup();
				}
		}
		
		function fwxImageLayer()
		{
			var activeItem = app.project.activeItem;
			var myNewSource = "D:\\temp\\facebook.png";
			app.beginUndoGroup(scriptName);
			if ((activeItem == null) || !(activeItem instanceof CompItem)) {
				alert("Please select or open a composition first.", scriptName);
			} else {
				var myFile = File(myNewSource);
				if (myFile) {
					var myImportOptions = new ImportOptions(myFile);
					var myFootage = app.project.importFile(myImportOptions);
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
		fileTextLayer();
		fwxImageLayer();
	}
	CreateTextLayers(this);
}
