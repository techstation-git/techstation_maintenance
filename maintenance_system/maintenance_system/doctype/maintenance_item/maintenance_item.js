// Copyright (c) 2020, Tech Station and contributors
// For license information, please see license.txt

frappe.ui.form.on("Maintenance Item", {
	customer: function (frm) {

		if (frm.doc.customer) {

			frappe.call({
				"method": "maintenance_system.maintenance_system.doctype.contact.getContact",
				args: {
					customer: frm.doc.customer,
					app_name: "customize_crm"
				},
				callback: function (r) {
					var len = r.message.length;
					for (var i = 0; i < len; i++) {
						frm.set_value("preferred_method_of_communication", r.message[i][0]);
						frm.set_value("phone", r.message[i][1]);
						frm.set_value("mobile_no", r.message[i][2]);
						frm.set_value("mobile_no_1", r.message[i][3]);
						frm.set_value("mobile_no_2", r.message[i][4]);
						frm.set_value("mobile_no_3", r.message[i][5]);
						frm.set_value("watsapp", r.message[i][6]);
						frm.set_value("telegram", r.message[i][7]);
					}
					cur_frm.refresh();
				}
			});
		}
	},
    item_status(frm){
        if(frm.doc.item_status){
            var text_data="";
            for(var i=0;i<frm.doc.item_status.length;i++){
                text_data+=frm.doc.item_status[i]["status"]+","
            }
            frm.set_value("item_statuss",text_data)
        }
    }
});


frappe.ui.form.on("Maintenance Item", {
	customer: function (frm) {
		cur_frm.refresh();
		cur_frm.refresh_fields();

		if (frm.doc.customer) {

			frappe.call({
				"method": "maintenance_system.maintenance_system.doctype.address.getAddress",
				args: {
					customer: frm.doc.customer,
					app_name: "customize_crm"
				},
				callback: function (r) {
					var len = r.message.length;
					for (var i = 0; i < len; i++) {
						frm.set_value("address", r.message[i][0]);
						frm.set_value("citytown", r.message[i][1]);
						frm.set_value("street", r.message[i][2]);
						frm.set_value("country", r.message[i][3]);
						frm.set_value("postal_code", r.message[i][4]);
						frm.set_value("house_number", r.message[i][5]);
						frm.set_value("apartment_number", r.message[i][6]);
						frm.set_value("floor", r.message[i][7]);
						frm.set_value("way_to_climb", r.message[i][8]);
						frm.set_value("special_marque", r.message[i][9]);
					}
					cur_frm.refresh();
				}
			});
		}
	}
});




frappe.ui.form.on('Maintenance Item', {
	refresh: function (frm) {
		var doc = frm.doc;
		
		$("[data-doctype='Receive Maintenance Item']").hide();
		if (doc.docstatus == 1) {
			frm.add_custom_button(__('Maintenance Order'),
				function () {
					frm.trigger("make_maintenance_order")
				}, __('Create'));
		}

		if (frm.doc.docstatus == 1) {
            frm.add_custom_button(__("Barcode"), function () {
                window.open("/printview?doctype=Maintenance%20Item&name=" + frm.doc.name + "&trigger_print=1&format=Barcode%20Maintenance%20Item&no_letterhead=1&letterhead=No%20Letterhead&settings=%7B%7D&_lang=en-US")
            }, __("Printing")).css({ 'backgroudcolor': 'black', 'font-weight': 'bold' });
            cur_frm.page.set_inner_btn_group_as_primary(__('Create'));
        }
	},
	make_receive_maintenance_items: function () {
		frappe.model.open_mapped_doc({
			method: "maintenance_system.maintenance_system.doctype.maintenance_item.maintenance_item.make_receive_maintenance_items",
			frm: cur_frm
		})
	},

	make_maintenance_order: function () {
		frappe.model.open_mapped_doc({
			method: "maintenance_system.maintenance_system.doctype.maintenance_item.maintenance_item.make_maintenance_order",
			frm: cur_frm
		})
	},
});



frappe.ui.form.on("Maintenance Item", "sales_invoice", function (frm) {
	cur_frm.set_query("sales_invoice", function () {
		return {
			"filters": {
				"customer": frm.doc.customer
			}
		};
	});
});

frappe.ui.form.on("Maintenance Item", "warranty_template", function (frm) {
	cur_frm.set_query("warranty_template", function () {
		return {
			"filters": {
				"enabled": 1
			}
		};
	});
});



frappe.ui.form.on("Maintenance Item", "sales_invoice", function (frm) {
	if (frm.doc.sales_invoice) {
		frappe.model.with_doc("Sales Invoice", frm.doc.sales_invoice, function () {
			cur_frm.clear_table("maintenance_invoice_items");
			var tabletransfer = frappe.model.get_doc("Sales Invoice", frm.doc.sales_invoice);
			$.each(tabletransfer.items, function (index, row) {
				var d = frm.add_child("maintenance_invoice_items");
				d.item_code = row.item_code;
				d.qty = row.qty;
				d.date = tabletransfer.posting_date;
				d.status = row.warranty_status;
				d.rate = row.rate;
				d.amount = row.amount;
				cur_frm.refresh_field("maintenance_invoice_items");
			});
		});
	}
});

frappe.ui.form.on('Maintenance Item', {
	item_sold_by_us: function (frm) {
		if (frm.doc.item_sold_by_us == 1) {
			frm.set_df_property('sales_invoice', 'reqd', 1);
			frm.set_df_property('item', 'reqd', 0);
			frm.set_value("sales_invoice", "");
			frm.set_value("item", "");
			cur_frm.clear_table("maintenance_invoice_items");
		}
		if (frm.doc.item_sold_by_us === 0) {
			frm.set_df_property('sales_invoice', 'reqd', 0);
			// frm.set_df_property('item', 'reqd', 1);
			frm.set_value("sales_invoice", "");
			frm.set_value("item", "");
			cur_frm.clear_table("maintenance_invoice_items");
		}
	}
});

frappe.ui.form.on('Maintenance Item', {
	onload: function (frm) {
		if (frm.doc.item_sold_by_us == 1) {
			frm.set_df_property('sales_invoice', 'reqd', 1);
			frm.set_df_property('item', 'reqd', 0);
		}
		if (frm.doc.item_sold_by_us === 0) {
			frm.set_df_property('sales_invoice', 'reqd', 0);
			// frm.set_df_property('item', 'reqd', 1);
		}
	}
});


frappe.ui.form.on('Maintenance Item', {
	warranty_status: function (frm) {
		if (frm.doc.warranty_status == "Enabled") {
			frm.set_df_property('warranty_template', 'reqd', 1);
		}
		if (frm.doc.warranty_status == "") {
			frm.set_df_property('warranty_template', 'reqd', 0);
		}
	}
});




//Address and Contact Display

frappe.ui.form.on('Maintenance Item', {
	onload: function (frm) {
		frm.set_query("customer_address", function () {
			if (frm.doc.customer) {
				return {
					query: 'frappe.contacts.doctype.address.address.address_query',
					filters: {
						link_doctype: "Customer",
						link_name: frm.doc.customer
					}
				};
			}
		})
		frm.set_query("contact", function () {
			if (frm.doc.customer) {
				return {
					query: 'frappe.contacts.doctype.contact.contact.contact_query',
					filters: {
						link_doctype: "Customer",
						link_name: frm.doc.customer
					}
				};
			}
		})
	},

	customer: function (frm) {
		if (frm.doc.customer) {
			frm.events.set_address_name(frm, 'Customer', frm.doc.customer);
			frm.events.set_contact_name(frm, 'Customer', frm.doc.customer);
		}
		else {
			frm.set_value('customer_address', '');
			frm.set_value('address_display', '');
			frm.set_value('contact', '');
			frm.set_value('contact_display', '');
            frm.set_value('mobile_no', '');
            frm.set_value('phone', '');
		}
	},
	set_address_name: function (frm, ref_doctype, ref_docname) {
		frappe.call({
			method: "maintenance_system.maintenance_system.doctype.maintenance_order.maintenance_order.get_address_name",
			args: {
				ref_doctype: ref_doctype,
				docname: ref_docname
			},
			callback: function (r) {
				if (r.message) {
					frm.set_value('customer_address', r.message);
				}
			}
		});
	},
	set_contact_name: function (frm, ref_doctype, ref_docname) {
		frappe.call({
			method: "maintenance_system.maintenance_system.doctype.maintenance_order.maintenance_order.get_contact_name",
			args: {
				ref_doctype: ref_doctype,
				docname: ref_docname
			},
			callback: function (r) {
				if (r.message) {
					frm.set_value('contact', r.message);
				}
			}
		});
	},
	customer_address: function (frm) {
		if (frm.doc.customer_address) {
			erpnext.utils.get_address_display(frm, 'customer_address', 'address_display', false);
		}
		if (!frm.doc.customer_address) {
			frm.set_value('address_display', '');
		}

	},
	contact: function (frm) {
		if (frm.doc.contact) {
			frm.events.get_contact_display(frm, frm.doc.contact);
		}
		if (!frm.doc.contact) {
			frm.set_value('contact_display', '');
		}
	},
	get_contact_display: function (frm, contact_name) {
		frappe.call({
			method: "frappe.contacts.doctype.contact.contact.get_contact_details",
			args: { contact: contact_name },
			callback: function (r) {
				if (r.message) {
					let contact_display = r.message.contact_display;
					if (r.message.contact_email) {
						contact_display += '<br>' + r.message.contact_email;

					}
					if (r.message.contact_phone) {
						contact_display += '<br>' + r.message.contact_phone;
						frm.set_value('phone', r.message.contact_phone);
					}
					if (r.message.contact_mobile && !r.message.contact_phone) {
						contact_display += '<br>' + r.message.contact_mobile;
						frm.set_value('mobile_no', r.message.contact_mobile);
					}
					frm.set_value('contact_display', contact_display);
				} else {
					frm.set_value('contact_display', '');
				}

			}
		});
	},
});
