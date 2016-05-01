
// Hold's the filepath of the source file currently displayed.
var g_filepath = null;

// Start and End line in source file currently displayed
var g_select_start = null; 
var g_select_end = null;

$(document).ready(function() {
	/*
	  When the user interacts with the databtable page buttons, it sends the requests data from the server
	 */
	var table = $('#bug_report').DataTable(
		{
            serverSide: true,
			"ajax" : {
				"url": "report",
				"type" : "POST",
				"data" : function(d) {
					d.report_id = $('#bug_report').attr('data-report-id')
				}
			},
			//"deferRender": true,
			"searching": false,
			"lengthChange": false,
			"autoWidth": false,
			"info": false,
			"columnDefs": [
				{ "width": "5%", "targets": 0 },
				{ "width": "20%", "targets": 1 },
				{ "width": "8%", "targets": 2 },
				{ "width": "12%", "targets": 7 },
				{ "width": "10%", "targets": 8 }
			]
		}
	);

	/*
	  When the user clicks on a row on the datatable, the handler gets the filepath from the row, and calls the method to display source code.
	 */
	table.on('click', 'tbody tr', function() {
		start_line = $(":nth-child(10)", this).text();
		end_line = $(":nth-child(11)", this).text();
		filepath = $(":last-child", this).text();
		display_source_file(filepath, start_line, end_line);
		$('#bug_info p').html('<Strong>Bug Message: </Strong>' + table.row(this).data()[3]);
	});
	
});

// jQuery.fn.redraw = function() {
//     return this.hide(0, function() {
//         $(this).show();
//     });
// };

/*
  When the user click's on a weakness (bug), this method changes the attribute:data-line in the prism object (class: line-numbers line-highlight) to highlight the particular lines.

Also, scrolls to the highlighted lines.
*/
function scroll_code(start_line, end_line){
	
	if(start_line != g_select_start || end_line != g_select_end) {

		$('.line-numbers').attr("data-line", start_line + "-" + end_line);
		//$('.line-highlight').parent().hide().show(0);
		//$('.line-numbers').parent().hide().show(0);

		//FIXME: I don't want to call the highlight method (which I guess reformats/redraws the whole prism object). I only want to change the highligting part.
		Prism.highlightAll();
		
		g_select_start = start_line;
		g_select_end = end_line;

		var container = $(".highlight");
		var scroll_to = $(".line-highlight");

		//FIXME: I am not satisfied with this, is there a better way to scroll in a container
		container.animate({
			scrollTop: scroll_to.offset().top - 200 - container.offset().top + container.scrollTop()
		});
	}
}

/*
  Gets the prism object's source language that has to be set based on the file extention
*/
function get_prism_language(filepath) {
	//Got the next line from here: http://stackoverflow.com/questions/190852/how-can-i-get-file-extensions-with-javascript
	var file_ext = filepath.slice((filepath.lastIndexOf(".") - 1 >>> 0) + 2);
	var file_lang = null;
	switch(file_ext) {
	case 'rb':
		file_lang = 'ruby';
		break;
	case 'py':
		file_lang = 'python';
		break;
	case 'c':
	case 'h':
		file_lang = 'clike';
		break;
	case 'cxx':
		file_lang = 'cpp';
		break;
	default:
		file_lang = file_ext;
	}

	return 'language-' + file_lang;
}

/*
Gets the source file from the server, and displays using prism
*/
function display_source_file(filepath, start_line, end_line) {

	if (filepath != g_filepath) {
		$.ajax({
			url : 'sourcefile',
			data : {'filepath' : filepath},
			dataType : 'text',
			success : function(data) {
				$('pre code').text(data);
				$('#source_code').html('<strong>Source File: </strong>' + filepath);
				
				$('#source_code').attr('class', 'line-numbers ' +
									   get_prism_language(filepath));

				g_select_start = null;
				g_select_end = null;

				scroll_code(parseInt(start_line), parseInt(end_line));
				g_filepath = filepath;
			}
		});
	} else {
		scroll_code(parseInt(start_line), parseInt(end_line));
	}
}

