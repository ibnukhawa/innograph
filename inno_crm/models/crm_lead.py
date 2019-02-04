# -*- coding: utf-8 -*-
""" Import """
from odoo import models, fields, api


class CRMLead(models.Model):
    """ Inherit CRM Lead"""
    _inherit = "crm.lead"

    stage_id = fields.Many2one('crm.stage', string='Stage',
                               track_visibility='onchange', index=True,
                               group_expand='_read_group_stage_ids',
                               default=lambda self: self._default_stage_id())

    @api.multi
    @api.onchange('lead_product_ids', 'lead_product_ids.price_unit')
    def _onchange_products_price_unit(self):
        """ Function to get Revenue from Total Amount Product Line """
        for lead in self:
            total = 0
            for line in lead.lead_product_ids:
                total += (line.price_unit * line.qty)
            lead.planned_revenue = total

    @api.multi
    def write(self, vals):
        """
            Extend write function to set stage based on Team/Probability
        """
        if 'team_id' in vals:
            stage_ids = self.env['crm.stage'].search([])
            stage_ids = stage_ids.filtered(lambda x: vals.get('team_id') in x.team_ids._ids)
            for stage in stage_ids.sorted('probability'):
                vals['stage_id'] = stage.id
                break
        if 'probability' in vals:
            prob = vals.get('probability')
            stage_id = self.env['crm.stage'].search([('probability', '>=', prob)],
                                                    order='probability', limit=1)
            if stage_id:
                vals['stage_id'] = stage_id.id
        return super(CRMLead, self).write(vals)

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        user_id = self._context.get('uid')
        user = self.env['res.users'].search([('id', '=', user_id)])
        if user.has_group('sales_team.group_sale_salesman'):
            res = super(CRMLead, self)._read_group_stage_ids(stages, domain, order)
            # If not sales manager will be filtered
            if not user.has_group('sales_team.group_sale_manager'):
                # Get user assigned team
                team_ids = self.env['crm.team'].search([])
                user_team = team_ids.filtered(lambda x: user_id in x.member_ids._ids)
                if not user_team:
                    return stages
                # Get stage assigned User's team
                stage_ids = self.env['crm.stage']
                for team in user_team:
                    stage_ids += res.filtered(lambda x: team.id in x.team_ids._ids)
                    res -= stage_ids
                stages = stage_ids
            else:
                return res
        return stages
