/*
	This file is part of ToeholdTools (a library for the analysis of
	toehold switch riboregulators created by the iGEM team City of
	London UK 2021).
	Copyright (c) 2021 Lucas Ng

	ToeholdTools is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	ToeholdTools is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with ToeholdTools.  If not, see <https://www.gnu.org/licenses/>.
*/

// eel.expose(log_js, 'log_js');
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
	$('#species_options_html')
		.append(html_to_insert)
		.dropdown({
			onChange: function (text, value) {
				update_FASTA_text();
			},
		});
}

async function update_FASTA_text() {
	// for displaying the FASTA selected from miRBase
	let text = await eel.get_FASTA_text_py($('#species_options_html').val())();
	$('textarea').val(text);
}

function set_dropdown_to_custom() {
	// for custom FASTA input
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
			FASTA_text: 'empty',
			temperature: 'decimal', // accepts integer values also
			max_size: 'integer',
			n_samples: 'integer',
		},
	});
}

async function update_pbar() {
	let next_trigger = await eel.next_trigger_py()();
	if (next_trigger !== 'StopIteration') {
		window.setTimeout(function () {
			$('.ui.progress').progress('increment', 1);
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
	scrollToElement('.ui.progress', 1000);
	await update_pbar();
	eel.send_result_py();
}

eel.expose(create_table_js, 'create_table_js');
function create_table_js(table_html, specificity) {
	$('#result_table').replaceWith(table_html);
	$('#speci_sub_header').html(specificity);
	if (document.getElementById('table_section').style.display === 'none') {
		$('#table_section').transition('fade', '2s');
	}
	$('#submit_button').removeClass('disabled loading'); // make submit button clickable again
	$('#download_link').attr(
		'download',
		$('#species_options_html').dropdown('get text') + '.csv'
	);
	scrollToElement('#table_section', 1000);
}

eel.expose(report_error_js, 'report_error_js');
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
