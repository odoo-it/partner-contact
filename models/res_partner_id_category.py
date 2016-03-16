# -*- coding: utf-8 -*-
#
# © 2004-2010 Tiny SPRL http://tiny.be
# © 2010-2012 ChriCar Beteiligungs- und Beratungs- GmbH
#             http://www.camptocamp.at
# © 2015 Antiun Ingenieria, SL (Madrid, Spain)
#        http://www.antiun.com
#        Antonio Espinosa <antonioea@antiun.com>
# ©  2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import api, models, fields
from openerp.exceptions import ValidationError, UserError
from openerp.tools.safe_eval import safe_eval
from openerp.tools.translate import _


class ResPartnerIdCategory(models.Model):
    _name = "res.partner.id_category"
    _order = "name"

    code = fields.Char(string="Code", size=16, required=True)
    name = fields.Char(string="ID name", required=True, translate=True)
    active = fields.Boolean(string="Active", default=True)
    validation_code = fields.Text(
        'Python validation code',
        help="Python code called to validate an id number.",
        default="""
# Python code. Use failed = True to .
# You can use the following variables :
#  - self: browse_record of the current ID Category browse_record
#  - id_number: browse_record of ID number to validte
"""
        )

    @api.multi
    def _validation_eval_context(self, id_number):
        self.ensure_one()
        return {'self': self,
                'id_number': id_number,
                }

    @api.multi
    def validate_id_number(self, id_number):
        """Validate the given ID number
        The method raises an openerp.exceptions.ValidationError if the eval of
        python validation code fails
        """
        self.ensure_one()
        eval_context = self._validation_eval_context(id_number)
        try:
            safe_eval(self.validation_code,
                      eval_context,
                      mode='exec',
                      nocopy=True)
        except Exception as e:
            raise UserError(
                _('Error when evaluating the id_category validation code:'
                  ':\n %s \n(%s)') % (self.name, e))
        if eval_context.get('failed', False):
            raise ValidationError(
                _("%s is not a valid %s identifier") % (
                    id_number.name, self.name))
