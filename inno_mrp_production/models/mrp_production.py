# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    sale_id = fields.Many2one('sale.order', 'Sales Order')
    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account", related='sale_id.related_project_id')
    date_scheduled = fields.Datetime('Scheduled Date', related='sale_id.date_scheduled')
    file_id = fields.Binary(related='sale_id.file_id', string="File Name")
    file_name = fields.Char(string="File Name")
    size_image = fields.Char(related='sale_id.size_image', string="Image Size")
    size_frame = fields.Char(related='sale_id.size_frame', string="Frame Size")
    size_print = fields.Char(related='sale_id.size_print', string="Print Size")
    finishing = fields.Char(related='sale_id.finishing')
    packing = fields.Char(related='sale_id.packing')
    proof = fields.Char()
    finishing_note = fields.Text(related='sale_id.finishing_note', string="Note")
    note = fields.Text()
    tasks_count = fields.Integer(compute='_compute_tasks_count')


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


class MrpWorkOrder(models.Model):
    _inherit = "mrp.workorder"

    sale_id = fields.Many2one('sale.order', related='production_id.sale_id', string="Sale Order")
    file_id = fields.Binary(string="File Name", related="production_id.file_id")
    file_name = fields.Char(string="File Name")
    size_image = fields.Char(string="Image Size", related="production_id.size_image")
    size_frame = fields.Char(string="Frame Size", related="production_id.size_frame")
    size_print = fields.Char(string="Print Size", related="production_id.size_print")
    finishing = fields.Char(related="production_id.finishing")
    packing = fields.Char(related="production_id.packing")
    finishing_note = fields.Text(string="Note", related="production_id.finishing_note")
    proof = fields.Char()
    task_ids = fields.One2many('project.task', 'workorder_id', string="Tasks")

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



class ProjectTask(models.Model):
    _inherit = 'project.task'

    workorder_id = fields.Many2one('mrp.workorder')