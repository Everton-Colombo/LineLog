import pickle

en = {"login_page": {"title": "Log in", "usr": "Username", "pw": "Password", "login_button": "Log in",
                     "invalid_credentials_popup_title": "Error", "invalid_credentials_popup_msg": "Please provide valid"
                                                                                                  " credentials",
                     "incorrect_usrname_popup_title": "Warning", "incorrect_usrname_popup_msg": "Incorrect Username",
                     "incorrect_pw_popup_title": "Warning", "incorrect_pw_popup_msg": "Incorrect Password"},
      "menu_bar": {"home": "Home", "sell": "Sell", "products": "Products", "costumers": "Costumers", "stats": "Stats",
                   "settings": "Settings", "log_out": "Log Out"},
      "home_page": {"title": "Home", "cur_usr": "Current User: ", "usr_role": "Role: ", "prods_frame_title": "Products",
                    "sales_frame_title": "Sales"},
      "sell_page": {"title": "Register Sale", "costumer_select_label": "Costumer: ", "search_popup_title": "Search",
                    "search_popup_cancel": "Cancel", "search_popup_select": "Select",
                    "not_mentioned_preval": "Not Mentioned", "add_prod_frame_title": "Add Product",
                    "quantity_label": "Quantity: ", "invalid_quant_popup_title": "Note",
                    "invalid_quant_popup_msg": "You can't select that quantity",
                    "receipt_frame_title": "Receipt", "total_label": "Total: ",
                    "remove_item_button": "Remove Item",
                    "cancel_sale_popup_title": "Cancel", "cancel_sale_popup_msg": "Are you sure you want to cancel "
                                                                                  "the sale?",
                    "proceed_unfinished_sale_popup_title": "Warning", "proceed_unfinished_sale_popup_msg": "Please make"
                                                                                                           " sure that "
                                                                                                           "you specify"
                                                                                                           " a costumer"
                                                                                                           " or registe"
                                                                                                           "red anythin"
                                                                                                           "g.",
                    "checkout_popup_title": "Checkout", "checkout_popup_receipt_frame_title": "Receipt",
                    "checkout_popup_total": "Total", "checkout_popup_paymethod_frame_title": "Payment Method",
                    "checkout_popup_paymethod_cash": "Cash", "checkout_popup_paymethod_debit": "Debit Card",
                    "checkout_popup_paymethod_credit": "Credit Card", "done_popup_title": "Done",
                    "done_popup_msg": "Sale registered successfully!"},
      "products_page": {"title": "Products", "search_prods_frame_title": "Search Products", "info_frame_title": "Info",
                        "info_frame_name": "Name: ", "info_frame_quantity": "Quantity: ", "info_frame_cost": "Cost: ",
                        "info_frame_retail_price": "Retail Price: ", "info_frame_profit_margin": "Profit Margin: ",
                        "edit_prod_button": "Edit Product", "edit_prod_popup_title": "Edit Product",
                        "edit_prod_name": "Name: ", "edit_prod_quantity": "Quantity: ",
                        "edit_prod_cost": "Cost (in cents): ", "edit_prod_retail_price": "Retail Price (in cents): ",
                        "edit_prod_profit_margin": "Profit Margin: ", "edit_prod_cancel": "Cancel",
                        "edit_prod_done": "Done", "edit_prod_done_popup_title": "Done",
                        "edit_prod_done_popup_msg": "Product edited successfully",
                        "edit_fail_name_popup_title": "Warning",
                        "edit_fail_name_popup_msg": "The name has already been assigned to another product",
                        "delete_prod_button": "Delete Product",
                        "delete_prod_popup_title": "Delete", "delete_prod_popup_msg": "Are you sure you want to delete "
                                                                                      "this product?",
                        "delete_error_popup_title": "Error", "delete_error_popup_msg": "Could not delete product: "
                                                                                       "product has active history",
                        "new_prod_button": "New Product", "new_prod_popup_title": "New Product",
                        "new_prod_name": "Name: ", "new_prod_initial_quantity": "Initial Quantity: ",
                        "new_prod_cost": "Cost (in cents): ", "new_prod_retail_price": "Retail Price (in cents): ",
                        "new_prod_profit_margin": "Profit Margin: ", "new_prod_cancel": "Cancel",
                        "new_prod_create": "Create", "new_prod_done_popup_title": "Done",
                        "new_prod_done_popup_msg": "Product added successfully",
                        "product_movement_frame_title": "Product Movement",
                        "new_prod_invalidvals_popup_title": "Value Error",
                        "new_prod_invalidvals_popup_msg": "The quantity, cost and retail price fields must be filled "
                                                          "with numbers, only"},
      "costumers_page": {"title": "Costumers", "search_costumers_frame_title": "Search Costumers",
                         "info_frame_title": "Info", "info_frame_name": "Name: ", "info_frame_phone": "Phone Number: ",
                         "info_frame_email": "E-Mail: ", "info_frame_bdate": "Birth Date: ",
                         "info_frame_gender": "Gender: ", "edit_costumer_button": "Edit Costumer",
                         "edit_costumer_popup_title": "Edit Costumer",
                         "edit_costumer_name": "Name: ", "edit_costumer_bdate": "Birth Date: ",
                         "edit_costumer_gender": "Gender: ", "edit_costumer_phone": "Phone Number: ",
                         "edit_costumer_email": "E-Mail: ", "edit_costumer_cancel": "Cancel",
                         "edit_costumer_done": "Done", "delete_costumer_button": "Delete Costumer",
                         "delete_costumer_popup_title": "Delete Costumer",
                         "delete_costumer_popup_msg": "Are you sure you want to delete this costumer?",
                         "delete_error_popup_title": "Error", "delete_error_popup_msg": "Unable to delete costumer: "
                                                                                        "costumer has active history",
                         "new_costumer_button": "New Costumer", "new_cotumer_popup_title": "New Costumer",
                         "new_costumer_name": "Name: ", "new_costumer_bdate": "Birth Date: ",
                         "new_costumer_gender": "Gender: ", "new_costumer_phone": "(Optional) Phone Number: ",
                         "new_costumer_email": "(Optional) E-Mail: ", "new_costumer_cancel": "Cancel",
                         "new_costumer_create": "Create", "new_costumer_invalidvals_popup_title": "Warning",
                         "new_costumer_invalidvals_popup_msg": "Please make sure the values are valid",
                         "new_costumer_success_popup_title": "Done",
                         "new_costumer_success_popup_msg": "Costumer added successfully",
                         "costumer_history_frame_title": "Costumer History",
                         "sales_history_defaults": "Sale ID | Date and Time | Total Price | Payment Method",
                         "sale_details_defaults": "Item Name | Quantity | Price"}}
# settings = {"language": "en"}
# with open("settings.config", 'wb') as file:
#     pickle.dump(settings, file)
#
with open("languages/en.lang", 'wb') as file:
  pickle.dump(en, file)
# TODO: add login errors to en
