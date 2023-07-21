from odoo import fields, models, api, _
from datetime import datetime
from odoo.exceptions import UserError
import csv
import base64


class ImportOrderWizard(models.TransientModel):
    _name = "import.order.wizard"
    _description = "Impoer order"

    @api.model
    def default_company(self):
        return self.env.company
    
    import_type = 'csv'
    file = fields.Binary(string="Plik", required=True)
    product_by = 'barcode'
    company_id = fields.Many2one('res.company','Company', default=default_company,required=True)
    unit_price = 'sheet'

    def show_success_msg(self, counter, confirm_rec, skipped_line_no):
        view = self.env.ref('order_message.order_message_wizard')
        context = dict(self._context or {})
        dic_msg = str(counter) + " Rekordy zostały pomyślnie zaimportowane \n"
        dic_msg = dic_msg + str(confirm_rec) + " Zapisy potwierdzone"
        if skipped_line_no:
            dic_msg = dic_msg + "\nNota:"
            for k, v in skipped_line_no.items():
                dic_msg = dic_msg + "\nWiersz Nr " + k + " " + v + " "
        else:
            dic_msg = dic_msg + "\nBrak pominiętych linii."
            context['message'] = dic_msg

        return {
            'name': 'Success',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'order.message.wizard',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': context,
        }

    def import_order_apply(self):
        sol_obj = self.env['sale.order.line']
        sale_order_obj = self.env['sale.order']
        skipped_line_no = {}

        if self:
            for rec in self:
                if rec.import_type == 'csv':
                    counter = 1
                    try:
                        file = str(base64.decodebytes(rec.file).decode('utf-8'))
                        myreader = csv.reader(file.splitlines())
                        next(myreader)

                        running_so = None
                        created_so = None
                        created_so_list_for_confirm = []
                        created_so_list = []

                        for row in myreader:
                            counter += 1

                            if row[0] and row[2]:
                                if row[0] != running_so:
                                    running_so = row[0]
                                    so_vals = {'name': running_so,
                                               'company_id': rec.company_id.id}

                                    partner_individual = self._find_or_create_partner(row[12], row[8], row[19])
                                    if not partner_individual:
                                        skipped_line_no[str(counter)] = " - Klient nie został utworzony. "
                                        continue

                                    partner_company = None
                                    if row[7]:
                                        partner_company = self._find_or_create_partner_company(row[6], row[7], row[8], row[18], row[21])
                                        if not partner_company:
                                            skipped_line_no[str(counter)] = " - Partner firmowy nie został utworzony. "
                                            continue
                                    else:
                                        partner_individual = self._find_or_create_partner(row[12], row[8], row[19])
                                        if not partner_individual:
                                            skipped_line_no[str(counter)] = " - Klient nie został utworzony. "
                                            continue

                                    invoice_address_partner = partner_company if partner_company else partner_individual
                                    invoice_address = self._find_or_create_invoice_address(invoice_address_partner.id, row[9], row[10], row[11], row[19])
                                    if not invoice_address:
                                        skipped_line_no[str(counter)] = " - Adres faktury nie został utworzony. "
                                        continue

                                    delivery_address = self._find_or_create_delivery_address(partner_individual.id, row[15], row[16], row[17], row[18], row[19])
                                    if not delivery_address:
                                        skipped_line_no[str(counter)] = " - Adres dostawy nie został utworzony. "
                                        continue


                                    if row[20]:
                                        pricelist = self._find_pricelist_by_currency(row[20])
                                        if not pricelist:
                                            skipped_line_no[str(counter)] = " - Nie znaleziono cennika dla podanej waluty. "
                                            continue
                                        so_vals.update({'pricelist_id': pricelist.id})

                                    if row[7]:
                                        so_vals.update({'partner_id': partner_individual.id, 'partner_invoice_id': partner_company.id})
                                    else:
                                        so_vals.update({'partner_id': partner_individual.id, 'partner_invoice_id': invoice_address.id})

                                    created_so = sale_order_obj.create(so_vals)
                                    created_so_list_for_confirm.append(created_so.id)
                                    created_so_list.append(created_so.id)

                                if created_so:
                                    product = self._find_product(row[2], rec.product_by)
                                    if not product:
                                        skipped_line_no[str(counter)] = " - Produkt nie został znaleziony. "
                                        continue

                                    uom = self._find_uom(row[4], product.uom_id)
                                    if not uom:
                                        skipped_line_no[str(counter)] = " - Jednostka miary nie została znaleziona. "
                                        continue

                                    vals = {
                                        'order_id': created_so.id,
                                        'product_id': product.id,
                                        'product_uom_qty': float(row[3]) if row[3] else 1.0,
                                        'product_uom': uom.id,
                                        'price_unit': float(row[5]) if row[5] else 0.0,
                                    }

                                    line = sol_obj.create(vals)

                                    if rec.unit_price == 'pricelist':
                                        line.product_uom_change()

                            else:
                                skipped_line_no[str(counter)] = " - Pole zamówienia sprzedaży lub produktu jest puste. "

                    except Exception as e:
                        raise UserError(_("Plik CSV ma niewłaściwy format: " + str(e)))

                    completed_records = len(created_so_list)
                    confirm_rec = len(created_so_list_for_confirm)
                    if skipped_line_no:
                        res = self.show_success_msg(completed_records, confirm_rec, skipped_line_no)
                    else:
                        res = self.show_success_msg(completed_records, confirm_rec, None)

                    return res

    def _find_or_create_partner(self, name, email, country):
        partner = self.env["res.partner"].search([('name', '=', name), ('email', '=', email), ('company_type', '=', 'person')], limit=1)
        if partner:
            return partner

        country = self.env["res.country"].search([('name', '=', country)], limit=1)
        partner_individual_vals = {
            'name': name,
            'customer_rank': 1,
            'email': email,
            'country_id': country.id,
            'company_type': 'person',
        }
        partner = self.env["res.partner"].create(partner_individual_vals)
        return partner
    
    def _find_or_create_delivery_address(self, parent_id, street, city, zip, phone, country_name):
        partner_obj = self.env["res.partner"]
        existing_delivery_address = partner_obj.search(
            [('type', '=', 'delivery'), ('parent_id', '=', parent_id), ('street', '=', street), ('city', '=', city),
             ('zip', '=', zip)], limit=1)
        if existing_delivery_address:
            return existing_delivery_address

        country = self.env["res.country"].search([('name', '=', country_name)], limit=1)
        delivery_address_vals = {
            'type': 'delivery',
            'parent_id': parent_id,
            'name': street,
            'street': street,
            'city': city,
            'zip': zip,
            'phone': phone,
            'country_id': country.id,
        }
        delivery_address = partner_obj.create(delivery_address_vals)
        return delivery_address

    def _find_or_create_partner_company(self, name, vat, email, phone, country_name):
        partner_obj = self.env["res.partner"]
        partner_company = partner_obj.search([('name', '=', name), ('vat', '=', vat), ('email', '=', email), ('company_type', '=', 'company')], limit=1)
        if partner_company:
            return partner_company

        country = self.env["res.country"].search([('name', '=', country_name)], limit=1)
        partner_company_vals = {
            'name': name,
            'customer_rank': 1,
            'email': email,
            'vat': vat,
            'phone': phone,
            'country_id': country.id,
            'company_type': 'company',
        }
        partner_company = partner_obj.create(partner_company_vals)
        return partner_company
    
    def _find_or_create_invoice_address(self, parent_id, street, city, zip, country_name):
        partner_obj = self.env["res.partner"]
        existing_invoice_address = partner_obj.search(
            [('type', '=', 'invoice'), ('parent_id', '=', parent_id), ('street', '=', street), ('city', '=', city),
            ('zip', '=', zip)], limit=1)
        if existing_invoice_address:
            return existing_invoice_address.parent_id

        country = self.env["res.country"].search([('name', '=', country_name)], limit=1)
        invoice_address_vals = {
            'type': 'invoice',
            'parent_id': parent_id,
            'name': street,
            'street': street,
            'city': city,
            'zip': zip,
            'country_id': country.id,
        }
        invoice_address = partner_obj.create(invoice_address_vals)
        return invoice_address.parent_id

    def _find_product(self, value, search_field):
        field_name = ''
        if search_field == 'name':
            field_name = 'name'
        elif search_field == 'int_ref':
            field_name = 'default_code'
        elif search_field == 'barcode':
            field_name = 'barcode'

        product = self.env['product.product'].search([(field_name, '=', value)], limit=1)
        return product
    
    def _find_uom(self, uom_name, default_uom):
        uom = self.env['uom.uom'].search([('name', '=', uom_name)], limit=1)
        return uom or default_uom
    
    def _find_pricelist_by_currency(self, currency_name):
        currency = self.env['res.currency'].search([('name', '=', currency_name)], limit=1)
        pricelist = self.env['product.pricelist'].search([('currency_id', '=', currency.id)], limit=1)
        return pricelist