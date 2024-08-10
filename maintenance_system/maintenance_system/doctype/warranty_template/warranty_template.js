// Copyright (c) 2020, Tech Station and contributors
// For license information, please see license.txt

frappe.ui.form.on('Warranty Template', {
	onload: function (frm) {
		if (!frappe.user_roles.includes("System Manager")) {
			cur_frm.set_df_property("warranty_bearing_rate", "read_only", 1)
			cur_frm.set_df_property("warranty_period_type", "read_only", 1)
			cur_frm.set_df_property("warranty_period", "read_only", 1)
		}
	},
	warranty_period_type(frm) {
		if (frm.doc.warranty_period_type === "") {
			frm.set_value("warranty_period", "");
		}
	},
	refresh(frm) {
		frm.set_df_property("warranty_period_type", "reqd", true);
		if (frm.doc.warranty_type == 'Partial Warranty') {
			frm.fields_dict.warranty_bearing_rate.grid.update_docfield_property("full_warranty", "read_only", 1);
		}
		else {
			frm.fields_dict.warranty_bearing_rate.grid.update_docfield_property("full_warranty", "read_only", 0);
		}
		//refresh_field("warranty_bearing_rate");
	},
	warranty_period(frm) {
		// if (frm.doc.warranty_type) {
		// 	frm.set_value("warranty_bearing_rate", "")
		// 	refresh_field("warranty_bearing_rate");
		// 	frm.trigger('warranty_type')
		// 	if (frm.doc.warranty_period_type == "Days") {
		// 		for (let i = 0; i < 1; i++) {
		// 			frappe.model.add_child(cur_frm.doc, "Warranty Template", "warranty_bearing_rate");
		// 			refresh_field("warranty_bearing_rate");
		// 		}


		// 	} else {
		// 		for (let i = 0; i < frm.doc.warranty_period; i++) {
		// 			let res = frappe.model.add_child(cur_frm.doc, "Warranty Template", "warranty_bearing_rate");
		// 			if (frm.doc.warranty_type == "Full Warranty") {
		// 				res.partial_warranty = 'Full Warranty'
		// 			}

		// 			refresh_field("warranty_bearing_rate");
		// 		}
		// 		frm.refresh_fields();

		// 	}

		// } else {
		// 	frm.set_value("warranty_period", "")
		// 	frm.set_value("warranty_bearing_rate", "")

		// 	frappe.msgprint("Please Select Warranty Period Type")
		// }

		frm.set_value("warranty_bearing_rate", "")
		refresh_field("warranty_bearing_rate");
		if (frm.doc.warranty_period_type == "Days") {
			for (let i = 0; i < 1; i++) {
				frappe.model.add_child(cur_frm.doc, "Warranty Template", "warranty_bearing_rate");
				refresh_field("warranty_bearing_rate");
			}


		} else {
			for (let i = 0; i < frm.doc.warranty_period; i++) {
				frappe.model.add_child(cur_frm.doc, "Warranty Template", "warranty_bearing_rate");

				refresh_field("warranty_bearing_rate");
			}
			frm.refresh_fields();

		}


	},
	// warranty_type(frm) {
	// 	console.log('TYpe->', frm.type);

	// 	if (frm.doc.warranty_type == 'Partial Warranty') {
	// 		frm.fields_dict.warranty_bearing_rate.grid.update_docfield_property("full_warranty", "read_only", 1);
	// 	}
	// 	else {
	// 		frm.fields_dict.warranty_bearing_rate.grid.update_docfield_property("full_warranty", "read_only", 0);
	// 	}

	// 	if (frm.type != frm.doc.warranty_type) {
	// 		let period = frm.doc.warranty_period
	// 		frm.set_value("warranty_period", "")
	// 		frm.set_value("warranty_period", period)
	// 	}

	// 	frm.fields_dict.warranty_bearing_rate.grid.update_docfield_property("partial_warranty", "Full Warranty");
	// 	var options = ["Item", "Service"]
	// 	if (frm.doc.warranty_type == 'Full Warranty') {
	// 		options.push("Full Warranty")
	// 	}
	// 	var df = frappe.meta.get_docfield("Warranty Bearing Rate", "partial_warranty", frm.doc.name);

	// 	df.options = options;

	// 	frm.type = frm.doc.warranty_type
	// 	frm.refresh_fields();
	// },
	validate(frm) {
		if (frm.doc.warranty_bearing_rate > 0) {
			if (frm.doc.warranty_period_type != "Days") {
				if (frm.doc.warranty_bearing_rate.length != frm.doc.warranty_period) {
					frappe.throw("Warranty Bearing Rate Should not greater than Warranty Period");
				}
			}

		}
	}
});

let check_data = (frm) => {
	let filter_accounts = frm.doc.warranty_bearing_rate.filter(item => {
		return item;
	});
	frm.doc.warranty_bearing_rate = [];
	filter_accounts.map(item => frm.add_child('warranty_bearing_rate', item));
	return filter_accounts.length;
};

frappe.ui.form.on("Warranty Bearing Rate", {
	full_warranty: function (frm, cdt, cdn) {
		var doc = locals[cdt][cdn]
		frappe.model.set_value(cdt, cdn, 'item', 0);
		frappe.model.set_value(cdt, cdn, 'services', 0);
	},
	item: function (frm, cdt, cdn) {
		var doc = locals[cdt][cdn]

		frappe.model.set_value(cdt, cdn, 'full_warranty', 0);
		frappe.model.set_value(cdt, cdn, 'services', 0);
	},
	services: function (frm, cdt, cdn) {
		var doc = locals[cdt][cdn]

		frappe.model.set_value(cdt, cdn, 'item', 0);
		frappe.model.set_value(cdt, cdn, 'full_warranty', 0);
	}
});




// CLIENT SCRIPT:

// frappe.ui.form.on('Warranty Template', {
//     warranty_period_type(frm){
//       if(frm.doc.warranty_period_type === ""){
//           frm.set_value("warranty_period","");
//       }  
//     },
//     refresh(frm){
//       frm.set_df_property("warranty_period_type","reqd",true); 
//     },
// 	warranty_period(frm) {
// 	    frm.doc.warranty_bearing_rate = [];
// 	    if(frm.doc.warranty_period_type == "Days"){
// 	        for(var i=0;i<1;i++){
// 	            frappe.model.add_child(cur_frm.doc, "Warranty Template", "warranty_bearing_rate");
//     	    }
//     	    refresh_field("warranty_bearing_rate");

// 	    }else{
// 	        for(var i=0;i<frm.doc.warranty_period;i++){
// 	            frappe.model.add_child(cur_frm.doc, "Warranty Template", "warranty_bearing_rate");
//     	    }
//     	    refresh_field("warranty_bearing_rate");
// 	    }

// 	    cur-frm.save()

// 	},
// 	validate(frm){
// 	  if(frm.doc.warranty_bearing_rate > 0){
// 	      if(frm.doc.warranty_period_type != "Days"){
//     	         if (frm.doc.warranty_bearing_rate.length != frm.doc.warrnty_period){
//     	             frappe.throw("Warranty Bearing Rate Should not greater than Warranty Period");
//     	        }
// 	      }

// 	  }  
// 	}
// });

// let check_data = (frm) => {
//     let filter_accounts = frm.doc.warranty_bearing_rate.filter(item => {
//             return item;
//     });
//     frm.doc.warranty_bearing_rate= [];
//     filter_accounts.map(item => frm.add_child('warranty_bearing_rate',item));
//     return filter_accounts.length;
// };






// 2

// frappe.ui.form.on('Warranty Template', {
// 	warranty_period_type(frm) {
// 		if (frm.doc.warranty_period_type === "") {
// 			frm.set_value("warranty_period", "");
// 		}
// 	},
// 	refresh(frm) {
// 		frm.set_df_property("warranty_period_type", "reqd", true);
// 	},
// 	warranty_period(frm) {
// 		if (frm.doc.warranty_type) {
// 			frm.doc.warranty_bearing_rate = [];
// 			frm.trigger('warranty_type')
// 			if (frm.doc.warranty_period_type == "Days") {
// 				for (let i = 0; i < 1; i++) {
// 					frappe.model.add_child(cur_frm.doc, "Warranty Template", "warranty_bearing_rate");
// 				}
// 				refresh_field("warranty_bearing_rate");

// 			} else {
// 				for (let i = 0; i < frm.doc.warranty_period; i++) {
// 					frappe.model.add_child(cur_frm.doc, "Warranty Template", "warranty_bearing_rate");
// 				}
// 				refresh_field("warranty_bearing_rate");
// 			}

// 		} else {
// 			// 			frm.doc.warranty_period = 0
// 			frm.set_value("warranty_period", "")
// 			frappe.throw("Please Select Warranty Period Type")
// 		}

// 		// 		cur_frm.save()
// 	},
// 	warranty_type(frm) {
// 		let options = ["", "Item", "Service"]
// 		if (frm.doc.warranty_type == 'Full Warranty') {
// 			options = ["Full Warranty"]
// 		}
// 		console.log(options);
// 		let df = frappe.meta.get_docfield("Warranty Bearing Rate", "partial_warranty", frm.doc.name);

// 		df.options = options;

// 		frm.refresh_fields();
// 	},
// 	validate(frm) {
// 		if (frm.doc.warranty_bearing_rate > 0) {
// 			if (frm.doc.warranty_period_type != "Days") {
// 				if (frm.doc.warranty_bearing_rate.length != frm.doc.warranty_period) {
// 					frappe.throw("Warranty Bearing Rate Should not greater than Warranty Period");
// 				}
// 			}

// 		}
// 	}
// });

// let check_data = (frm) => {
// 	let filter_accounts = frm.doc.warranty_bearing_rate.filter(item => {
// 		return item;
// 	});
// 	frm.doc.warranty_bearing_rate = [];
// 	filter_accounts.map(item => frm.add_child('warranty_bearing_rate', item));
// 	return filter_accounts.length;
// };
