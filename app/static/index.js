$(document).ready(function() {
	/*
	  As soon as the index.html is ready, the datatable that is supposed to display 
	  the summary information sends a POST request to the route: assessment for summary data
	*/
	var table = $('#assessments').DataTable(
		{
            serverSide: true,
			"ajax" : {
				"url": "assessments",
				"type" : "POST",
			},
		}
	);

	/*
	  Event handler that gets triggered when the user clicks on a row in the datatable. The event handler function gets the assessment metadata from the table and sends a post request to the route: results. 
	*/
	/*
	  FIXME: This uses a hidden form which feels like an ameture idea. Is there a better way to POST a request and replace (get) the whole page?
	*/
	table.on('click', 'tbody tr', function() {	
		var pkg_name = $(this).find("td:nth-child(2)").text()
		var pkg_ver = $(this).find("td:nth-child(3)").text()
		var plat = $(this).find("td:nth-child(5)").text()
		var tool_type = $(this).find("td:nth-child(6)").text()
		var tool_ver = $(this).find("td:nth-child(7)").text()

		$('#hidden-form').append(
			$('#hidden-form').add($('<input type="text" name="package_short_name">').val(pkg_name)), 
			$('#hidden-form').add($('<input type="text" name="package_version">').val(pkg_ver)), 
			$('#hidden-form').add($('<input type="text" name="platform">').val(plat)),
			$('#hidden-form').add($('<input type="text" name="tool_type">').val(tool_type)),
			$('#hidden-form').add($('<input type="text" name="tool_version">').val(tool_ver))
		);
		
		$("form input[type=\"submit\"]").trigger("click");

	});
});
