# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    sale_id = fields.Many2one('sale.order', 'Sales')
    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account", related='sale_id.related_project_id')
    date_scheduled = fields.Datetime('Scheduled Date', related='sale_id.date_scheduled')
    file_id = fields.Binary(related='sale_id.file_id', string="File Name")
    size_image = fields.Char(related='sale_id.size_image', string="Image Size")
    size_frame = fields.Char(related='sale_id.size_frame', string="Frame Size")
    size_print = fields.Char(related='sale_id.size_print', string="Print Size")
    finishing = fields.Char(related='sale_id.finishing')
    packing = fields.Char(related='sale_id.packing')
    proof = fields.Char()
    finishing_note = fields.Char(related='sale_id.finishing_note', string="Note")
    note = fields.Text()


    @api.multi
    @api.depends('move_raw_ids')
    def _has_moves(self):
        super(MrpProduction, self)._has_moves()
        for mo in self:
            mo.has_moves = any([mv.state != 'cancel' for mv in mo.move_raw_ids])

    @api.multi
    def set_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def action_open_project(self):
        self.ensure_one()
        project = False
        if self.analytic_account_id and self.analytic_account_id.project_ids:
            project = self.analytic_account_id.project_ids[0]
        if project:
            return {
                'name': _("Project"),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'project.project',
                'target': 'current',
                'res_id': project.id,
            }
        return False

    @api.multi
    def action_open_sale(self):
        self.ensure_one()
        sale_id = self.sale_id
        if sale_id:
            return {
                'name': _("Sale Order"),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'sale.order',
                'target': 'current',
                'res_id': sale_id.id,
            }
        return False

    @api.multi
    def button_mark_done(self):
        self.ensure_one()
        res = super(MrpProduction, self).button_mark_done()
        if self.location_dest_id.display_name != 'WHFG/Stock':
            # get destination location
            loc_obj = self.env['stock.location']
            loc_dst_id = False
            # Get WHFG Location
            parent_src = loc_obj.search([('usage', '=', 'view'), 
                ('name', '=', 'WHFG')], limit=1)
            if parent_src:
                location_src = loc_obj.search([('location_id', '=', parent_src.id), ('name', 'like', 'Stock')], limit=1)
                if location_src:
                    loc_dst_id = location_src

            if loc_dst_id:
                # get source location
                loc_id = self.location_dest_id
                # get picking type
                picking_type = self.env['stock.picking.type'].search([('code', '=', 'internal'), 
                    ('default_location_src_id', '=', loc_id.id)])
                # Create Internal Transfer
                vals = {
                    'location_id': loc_id.id,
                    'location_dest_id': loc_dst_id.id,
                    'min_date': self.date_scheduled,
                    'origin': self.name,
                    'picking_type_id': picking_type.id,
                }
                int_pick = self.env['stock.picking'].create(vals)
                # Add stock move to picking
                move_ids = self.move_finished_ids.copy()
                for move in move_ids:
                    move.write({
                            'location_id': loc_id.id,
                            'location_dest_id': loc_dst_id.id,
                            'picking_type_id': picking_type.id,
                            'picking_id': int_pick.id,
                            'production_id': False
                        })
                int_pick.action_confirm()
                int_pick.action_assign()
                # Set done qty 
                for line in int_pick.pack_operation_product_ids:
                    line.qty_done = line.product_qty
                int_pick.do_new_transfer()
        return res
