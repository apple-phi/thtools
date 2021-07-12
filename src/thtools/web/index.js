// eel.expose(log_js);
// function log_js(x) {
// 	console.log(x);
// }

async function add_species() {
	let species_list = await eel.species_options_py()();
	let html_to_insert = '';
	for (let i = 0; i < species_list.length; i++) {
		html_to_insert +=
			'<option value="' +
			species_list[i] +
			'">' +
			species_list[i] +
			'</option>';
	}
	$('#species_options_html').append(html_to_insert).dropdown();
}

async function update_FASTA_text() { // for displaying the FASTA selected from miRBase
	let text = await eel.get_FASTA_text_py($('#species_options_html').val())();
	$('textarea').val(text);
}

function set_dropdown_to_custom() { // for custom FASTA input
	$('#species_options_html')
		.dropdown('restore defaults', true)
		.dropdown('set text', 'Custom');
}

function setup_form_rules() {
	$.fn.form.settings.rules.is_ths = function (value) {
		return $.fn.form.settings.rules.regExp(
			value,
			'/^[GUAC]+' + $('#main_form').form('get value', 'rbs') + '[GUAC]+$/gi'
		);
	};
	$('#main_form').form({
		fields: {
			ths: 'is_ths',
			rbs: 'regExp[/^[GUAC]+$/gi]',
			FASTA_txt: 'empty',
			temperature: 'decimal', // accepts integer values also
			max_size: 'integer',
			n_samples: 'integer',
		},
	});
}

async function update_pbar() {
	let chunk_len = await eel.next_chunk_len_py()();
	if (chunk_len !== 'StopIteration') {
		window.setTimeout(function () {
			$('.ui.progress').progress('increment', chunk_len);
		});
		await update_pbar();
	}
}

async function run_test() {
	$('#submit_button').addClass('disabled loading'); // makes submit button unclickable
	if (document.getElementById('pbar_section').style.display === 'none') {
		$('#pbar_section').transition('fade', '2s');
	}
	let data = $('#main_form')
		.serializeArray()
		.reduce(function (obj, item) {
			// https://stackoverflow.com/a/24012884/13712044
			obj[item.name] = item.value;
			return obj;
		}, {});
	await eel.accept_data_py(data);
	let FASTA_num = await eel.FASTA_num_py()();
	$('.ui.progress')
		.progress({
			total: FASTA_num,
			precision: 0.1,
			text: {
				active: '{value} of {total} miRNAs tested',
				success: '{total} miRNAs tested!',
			},
		})
		.progress('set active')
		.progress('reset');
	await eel.run_test_py();
	await update_pbar();
	eel.send_results_py();
}

////////////////////////////////////////////////////////////////
function scrollToElement(element, duration) { //https://stackoverflow.com/a/39494245/13712044
	function getElementY(query) {
		return window.pageYOffset + document.querySelector(query).getBoundingClientRect().top;
	}
	let startingY = window.pageYOffset;
	let elementY = getElementY(element);
	// If element is close to page's bottom then window will scroll only to some position above the element.
	let targetY = document.body.scrollHeight - elementY < window.innerHeight ? document.body.scrollHeight - window.innerHeight : elementY;
	let diff = targetY - startingY;
	// Easing function: easeInOutCubic
	// From: https://gist.github.com/gre/1650294
	let easing = (t) =>
		t < 0.5 ? 4 * t * t * t : (t - 1) * (2 * t - 2) * (2 * t - 2) + 1;
	let start;
  
	if (!diff) {
		return;
	}
  
	// Bootstrap our animation - it will get called right before next frame shall be rendered.
	window.requestAnimationFrame(function step(timestamp) {
		if (!start) {
			start = timestamp;
		}
		// Elapsed miliseconds since start of scrolling.
		let time = timestamp - start;
			// Get percent of completion in range [0, 1].
		let percent = Math.min(time / duration, 1);
		// Apply the easing.
		// It can cause bad-looking slow frames in browser performance tool, so be careful.
		percent = easing(percent);

		window.scrollTo(0, startingY + diff * percent);

			// Proceed with animation as long as we wanted it to.
		if (time < duration) {
			window.requestAnimationFrame(step);
		}
	});
}
////////////////////////////////////////////////////////////////

eel.expose(create_table_js);
function create_table_js(table_html, specificity) {
	// $('.ui.progress').progress('complete');
	$('#results_table').replaceWith(table_html);
	$('#speci_sub_header').html(specificity);
	if (document.getElementById('table_section').style.display === 'none') {
		$('#table_section').transition('fade', '2s');
	}
	// $('#pbar_segment').transition('jiggle', '500ms');
	$('#submit_button').removeClass('disabled loading'); // make submit button clickable again
	scrollToElement('#table_section', 1000);
}

eel.expose(report_error_js);
function report_error_js(msg) {
	$('#error_msg').text(msg);
	$('.ui.basic.modal').modal('show');
}

$(document).ready(function () {
	eel.print_py('JS loaded');

	add_species();
	setup_form_rules();
	document.getElementById('main_form').onsubmit = function () {
		if ($('#main_form').form('is valid')) {
			run_test();
		}
		return false;
	};
});
