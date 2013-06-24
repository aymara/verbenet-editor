/* jQuery editable Copyright Dylan Verheul <dylan@dyve.net>
 * Licensed like jQuery, see http://docs.jquery.com/License
 */

$.fn.editable = function(url, options) {
	// Options
	options = arrayMerge({
		"url": url,
		"paramName": "classe",
		"callback": null,
		"saving": "saving ...",
		"type": "text",
		"submitButton": 0,
		"delayOnBlur": 0,
		"extraParams": {},
		"editClass": null,
        "edited": this
	}, options);

	// Set up
	this.click(function(e) {
			if (this.editing) return;
			if (!this.editable) this.editable = function() {
				var that = this;
				that.editing = true;
				options.edited.orgHTML = $(options.edited).html();
				options.edited.innerHTML = "";
				if (options.editClass) $(options.edited).addClass(options.editClass);
				var f = document.createElement("form");
				var i = createInputElement(options.edited.orgHTML);
				var t = 0;
				f.appendChild(i);
				if (options.submitButton) {
					var b = document.createElement("input");
					b.type = "submit";
					b.value = "OK";
					f.appendChild(b);
				}
				options.edited.appendChild(f);
				i.focus();
				$(i).blur(
						options.delayOnBlur ? function() { t = setTimeout(reset, options.delayOnBlur) } : reset
					)
					.keydown(function(e) {
						if (e.keyCode == 27) { // ESC
							e.preventDefault;
							reset
						}
					});
				$(f).submit(function(e) {
					if (t) clearTimeout(t);
					e.preventDefault();
					var p = {};
					p[i.name] = $(i).val();
					$(options.edited).html(options.saving).load(options.url, arrayMerge(options.extraParams, p), function() {
						// Remove script tags
						options.edited.innerHTML = options.edited.innerHTML.replace(/<\s*script\s*.*>.*<\/\s*script\s*.*>/gi, "");
						// Callback if necessary
						if (options.callback) options.callback(options.edited); 
						// Release
						that.editing = false;						
					});
				});
				function reset() {
					options.edited.innerHTML = options.edited.orgHTML;
					if (options.editClass) $(options.edited).removeClass(options.editClass);
					that.editing = false;					
				}
			};
			this.editable();
		})
	;
	// Don't break the chain
	return this;
	// Helper functions
	function arrayMerge(a, b) {
		if (a) {
			if (b) for(var i in b) a[i] = b[i];
			return a;
		} else {
			return b;		
		}
	};
	function createInputElement(v) {
		if (options.type == "textarea") {
			var i = document.createElement("textarea");
			options.submitButton = true;
			options.delayOnBlur = 100; // delay onBlur so we can click the button
		} else {
			var i = document.createElement("input");
			i.type = "text";
		}
		$(i).val(v);
		i.name = options.paramName;
		return i;
	}
};
