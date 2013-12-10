{
	// Create Text Layers.jsx
	// 
	// This script scales the selected layers within the active comp.
	//
	// First, it prompts the user for a text_factor.
	// Next, it scales all selected layers, including cameras.

	function CreateTextLayers(thisObj)
	{
		var scriptName = "Create Text Layers";
		var value = "";
		var myText = "";
		//
		// This function is called when the user enters text for the scale.
		//
		function on_textInput_changed()
		{
			// Set the text_factor based on the text
			//value = thisObj.text;
			value = this.parent.parent.optsRow.text_input.text;
			if(value !== '' && !isNaN(value)) {
				alert(value + " is not a string. Please enter a string.", scriptName);
			}
		}
		
		function onskTextClick()
		{
			var activeItem = app.project.activeItem;
			var myLayers = activeItem.selectedLayers;
			var layerName = myLayers[0].name;
			//var theValue = activeItem.selectedLayers[0].sourceText.value;
			layerName = layerName.split(".")
			alert(layerName[0]);
		}

		function onTextClick()
		{
			var activeItem = app.project.activeItem;
			value = this.parent.parent.optsRow.text_input.text;

			if ((activeItem == null) || !(activeItem instanceof CompItem)) {
				alert("Please select or open a composition first.", scriptName);
				} else {

					// Validate the input field, in case the user didn't defocus it first (which often can be the case).
					this.parent.parent.optsRow.text_input.notify("onChange");

					//var activeComp = activeItem;

					// By bracketing the operations with begin/end undo group, we can 
					// undo the whole script with one undo operation.
					app.beginUndoGroup(scriptName);
					// Create a text layer.
					
					myText = activeItem.layers.addText(value);
					

					myText.position.setValue( [ 100, 200 ] );
					myText.scale.setValue( [ 500, 500 ] );

					//var myPosition = activeItem.layers.property("position");
					//myPosition.setValueAtTime(1,[100,100]);
					//alert ("myText.transform ", myText.property("position"));
					//myText("justification") = "center";
					app.endUndoGroup();

					// Reset text_factor to "Enter text here" for next use.
					this.parent.parent.optsRow.text_input.text = "Enter text here";
				}
		}

		// 
		// This function puts up a modal dialog asking for a text_factor.
		// Once the user enters a value, the dialog closes, and the script scales the comp.
		// 
		function BuildAndShowUI(thisObj)
		{
			// Create and show a floating palette.
			var my_palette = (thisObj instanceof Panel) ? thisObj : new Window("palette", scriptName, undefined, {resizeable:true});
			if (my_palette != null)
			{
				var res = 
					"group { \
						orientation:'column', alignment:['fill','top'], alignChildren:['left','top'], spacing:5, margins:[0,0,0,0], \
						optsRow: Group { \
							orientation:'column', alignment:['fill','top'], \
							text_input: EditText { text:'enter text here', alignment:['left','top'], preferredSize:[100,20] }, \
						}, \
						cmds: Group { \
							alignment:['fill','top'], \
							okButton: Button { text:'Create Text Layer', alignment:['fill','center'] }, \
							skButton: Button { text:'Show layer name', alignment:['fill','center'] }, \
						}, \
					}";

				my_palette.margins = [10,10,10,10];
				my_palette.grp = my_palette.add(res);
				
				// Workaround to ensure the edittext text color is black, even at darker UI brightness levels.
				var winGfx = my_palette.graphics;
				var darkColorBrush = winGfx.newPen(winGfx.BrushType.SOLID_COLOR, [0,0,0], 1);
				my_palette.grp.optsRow.text_input.graphics.foregroundColor = darkColorBrush;
				
				// Set the callback. When the user enters text, this will be called.
				//my_palette.grp.optsRow.text_input.onChange = on_textInput_changed;

				my_palette.grp.cmds.okButton.onClick = onTextClick;
				my_palette.grp.cmds.skButton.onClick = onskTextClick;

				my_palette.layout.layout(true);
				my_palette.layout.resize();
				my_palette.onResizing = my_palette.onResize = function () {this.layout.resize();}
			}
			return my_palette;
		}

		// 
		// The main script.
		//
		if (parseFloat(app.version) < 8) {
			alert("This script requires After Effects CS3 or later.", scriptName);
			return;
		}
		
		var my_palette = BuildAndShowUI(thisObj);
		if (my_palette != null) {
			if (my_palette instanceof Window) {
				my_palette.center();
				my_palette.show();
			} else {
				my_palette.layout.layout(true);
			}
		} else {
			alert("Could not open the user interface.", scriptName);
		}
	}
	
	CreateTextLayers(this);
}
