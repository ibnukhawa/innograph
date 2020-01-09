# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    sale_id = fields.Many2one('sale.order', 'Sales Order')
    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account", related='sale_id.related_project_id')
    date_scheduled = fields.Datetime('Scheduled Date', related='sale_id.date_scheduled')
    file_loc = fields.Text(related='sale_id.file_loc', string="File Location")
    size_image = fields.Char(related='sale_id.size_image', string="Image Size")
    size_frame = fields.Char(related='sale_id.size_frame', string="Frame Size")
    size_print = fields.Char(related='sale_id.size_print', string="Print Size")
    finishing = fields.Char(related='sale_id.finishing')
    packing = fields.Char(related='sale_id.packing')
    proof = fields.Char(related='sale_id.proof')
    finishing_note = fields.Text(related='sale_id.finishing_note', string="Note")
    note = fields.Text()
    tasks_count = fields.Integer(compute='_compute_tasks_count')
    partner_id = fields.Many2one('res.partner', related='sale_id.partner_id')

    @api.model
    def default_get(self, fields):
        """ Change Default Picking Type to WHFG Picking Type """
        res = super(MrpProduction, self).default_get(fields)
        warehouse_obj = self.env['stock.warehouse']
        warehouse = warehouse_obj.search([('code', '=', 'WHFG')], limit=1)
        if warehouse:
            pick_type = self.env['stock.picking.type'].search([('code', '=', 'mrp_operation'), 
                ('warehouse_id.company_id', 'in', [self.env.context.get('company_id', self.env.user.company_id.id), False]),
                ('warehouse_id', '=', warehouse.id)], limit=1)
            if pick_type:
                res['picking_type_id'] = pick_type.id
                res['location_src_id'] = pick_type.default_location_src_id.id
                res['location_dest_id'] = pick_type.default_location_dest_id.id
        return res

    @api.multi
    @api.depends('move_raw_ids')
    def _has_moves(self):
        super(MrpProduction, self)._has_moves()
        for mo in self:
            mo.has_moves = any([mv.state != 'cancel' for mv in mo.move_raw_ids])

    @api.multi
    def set_draft(self):
        self.write({'state': 'draft'})
        for mo in self:
            mo.move_finished_ids.unlink()
            mo.move_raw_ids.unlink()
            mo.workorder_ids.unlink()

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
    def _compute_tasks_count(self):
        for mo in self:
            task_ids = mo.workorder_ids.mapped('task_ids')
            mo.tasks_count = len(task_ids)

    @api.multi
    def action_view_tasks(self):
        workorder_ids = self.mapped('workorder_ids')
        task_ids = workorder_ids.mapped('task_ids')
        action = self.env.ref('project.action_view_task').read()[0]
        if len(task_ids) > 1:
            action['domain'] = [('id', 'in', task_ids.ids)]
        elif len(task_ids) == 1:
            action['views'] = [(self.env.ref('project.view_task_form2').id, 'form')]
            action['res_id'] = task_ids.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        action['context'] = self.env.context
        return action

    @api.multi
    def button_mark_done(self):
        self.ensure_one()
        res = super(MrpProduction, self).button_mark_done()
        if self.location_dest_id.display_name != 'WHFG/Stock':
            # get destination location
            loc_obj = self.env['stock.location']
            loc_dst_id = False
            # Get WHFG Location
            whfg_loc = self.env.user.company_id.default_finished_product_location
            loc_dst_id = whfg_loc or self.env.ref('stock.stock_location_stock')

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

    def action_create_part_request(self):
        req_part = self.env['mrp.part.request']
        req_part_src = req_part.search([('bom_id', '=', self.bom_id.id), 
                                        ('production_id', '=', self.id), 
                                        ('state', 'not in', ['done'])], limit=1)
        action = self.env.ref('inno_mrp_production.action_mrp_part_request').read()[0]
        action['views'] = [(self.env.ref('inno_mrp_production.mrp_part_request_form_view').id, 'form')]

        if req_part_src:
            action['views'] = [(self.env.ref('inno_mrp_production.mrp_part_request_form_view').id, 'form')]
            action['res_id'] = req_part_src.id
        else:                
            ctx = self.env.context.copy()
            ctx['default_product_id'] = self.product_id.product_tmpl_id.id
            ctx['default_bom_id'] = self.bom_id.id
            ctx['default_production_id'] = self.id
            ctx['default_location_dest_id'] = self.location_src_id.id    
            action['context'] = ctx
        return action

    @api.multi
    def action_cancel(self):
        part_req = self.env['mrp.part.request'].search([('production_id', 'in', self.ids)])
        if part_req.filtered(lambda r: r.state in ['confirm', 'done']):
            raise UserError(_("You cannot cancel this Manufacturing Order because it has Material Request with status in Confirmed / Done."))
        else:
            part_req.unlink()
        return super(MrpProduction, self).action_cancel()

    def _generate_raw_move(self, bom_line, line_data):
        res = super(MrpProduction, self)._generate_raw_move(bom_line, line_data)
        res.qty_initial = line_data['qty']
        return res


class MrpWorkOrder(models.Model):
    _inherit = "mrp.workorder"

    sale_id = fields.Many2one('sale.order', related='production_id.sale_id', string="Sale Order")
    file_loc = fields.Text(string="File Location", related="production_id.file_loc")
    size_image = fields.Char(string="Image Size", related="production_id.size_image")
    size_frame = fields.Char(string="Frame Size", related="production_id.size_frame")
    size_print = fields.Char(string="Print Size", related="production_id.size_print")
    finishing = fields.Char(related="production_id.finishing")
    packing = fields.Char(related="production_id.packing")
    finishing_note = fields.Text(string="Note", related="production_id.finishing_note")
    proof = fields.Char(related='sale_id.proof')
    task_ids = fields.One2many('project.task', 'workorder_id', string="Tasks")
    partner_id = fields.Many2one('res.partner', related='sale_id.partner_id')
    workorder_part_ids = fields.One2many('mrp.workorder.part', 'workorder_id', string="Consumed Material")

    @api.multi
    def action_view_sales(self):
        sales = self.mapped('sale_id')
        action = self.env.ref('sale_approval.action_orders_extends').read()[0]
        if len(sales) > 1:
            action['domain'] = [('id', 'in', sales.ids)]
        elif len(sales) == 1:
            action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
            action['res_id'] = sales.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        action['context'] = self.env.context
        return action

    @api.multi
    def action_view_tasks(self):
        tasks = self.mapped('task_ids')
        action = self.env.ref('project.action_view_task').read()[0]
        
        context = self.env.context.copy()
        mo_number = self.mapped('production_id')[0].name
        product = self.mapped('product_id')[0].display_name 
        context['default_name'] = "%s - %s" % (mo_number, product)
        context['default_date_deadline'] = self.mapped('production_id')[0].date_scheduled
        context['default_workorder_id'] = self.mapped('id')[0]
        action['context'] = context
        
        if len(tasks) > 1:
            action['domain'] = [('id', 'in', tasks.ids)]
        elif len(tasks) == 1:
            action['views'] = [(self.env.ref('project.view_task_form2').id, 'form')]
            action['res_id'] = tasks.ids[0]
        else:
            action['views'] = [(self.env.ref('project.view_task_form2').id, 'form')]
        return action

    @api.multi
    def button_start(self):
        self.ensure_one()
        res = super(MrpWorkOrder, self).button_start()
        wo_part_obj = self.env['mrp.workorder.part']
        parts = []
        for move in self.move_raw_ids:
            vals = {
                'product_id': move.product_id.id,
                'name': move.product_id.display_name,
                'quantity': move.product_uom_qty,
                'uom_id': move.product_uom.id,
                'move_id': move.id,
            }
            new_part = wo_part_obj.create(vals)
            parts.append(new_part.id)
        self.write({'workorder_part_ids': [(6, 0, parts)]})
        return res

    @api.multi
    def record_production(self):
        self.ensure_one()
        res = super(MrpWorkOrder, self).record_production()
        self._update_move_raw_ids()
        return res

    @api.multi
    def button_finish(self):
        self.ensure_one
        res = super(MrpWorkOrder, self).button_finish()
        self._update_move_raw_ids()
        return res

    @api.multi
    def _update_move_raw_ids(self):
        self.production_id.button_unreserve()
        for move in self.move_raw_ids:
            consume = self.workorder_part_ids.filtered(lambda w: w.move_id.id == move.id)
            vals = {}
            if not consume:
                vals['ordered_qty'] = 0
                vals['product_uom_qty'] = 0
                vals['quantity_done'] = 0
            else:
                new_qty = consume.uom_id._compute_quantity(consume.quantity, move.product_uom)
                vals['ordered_qty'] = new_qty
                vals['product_uom_qty'] = new_qty
                vals['quantity_done'] = new_qty
            move.write(vals)
        self.production_id.action_assign()



class ProjectTask(models.Model):
    _inherit = 'project.task'

    workorder_id = fields.Many2one('mrp.workorder')


class MrpWorkorderPart(models.Model):
    _name = 'mrp.workorder.part'

    workorder_id = fields.Many2one('mrp.workorder', string="Workorder")
    product_id = fields.Many2one('product.product', string="Product")
    name = fields.Char(string="Description")
    quantity = fields.Float()
    uom_id = fields.Many2one('product.uom', string="Unit of Measure")
    move_id = fields.Many2one('stock.move', string="Related Move")