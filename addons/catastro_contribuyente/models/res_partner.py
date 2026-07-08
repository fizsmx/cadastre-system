from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_contribuyente = fields.Boolean(string="Es Contribuyente", default=False)
    con_pmc = fields.Integer(string="Padrón Municipal (PMC)", readonly=True, copy=False)
    pmc_ant = fields.Char(string="PMC Anterior")
    con_tipo = fields.Selection([
        ('PER', 'Persona Natural'),
        ('EMP', 'Persona Jurídica/Empresa')
    ], string="Tipo de Contribuyente", default='PER')
    
    con_nit = fields.Char(string="NIT")
    doc_tipo = fields.Selection([
        ('CI', 'Cédula de Identidad'),
        ('RUN', 'RUN'),
        ('PAS', 'Pasaporte'),
        ('NIT', 'NIT')
    ], string="Tipo de Documento")
    doc_num = fields.Char(string="Número de Documento")
    doc_exp = fields.Selection([
        ('LP', 'La Paz'),
        ('CB', 'Cochabamba'),
        ('SC', 'Santa Cruz'),
        ('OR', 'Oruro'),
        ('PT', 'Potosí'),
        ('TJ', 'Tarija'),
        ('CH', 'Chuquisaca'),
        ('BE', 'Beni'),
        ('PD', 'Pando')
    ], string="Expedido en")
    
    con_fech_ini = fields.Date(string="Fecha Inicio de Actividad")
    con_fecnac = fields.Date(string="Fecha de Nacimiento")
    
    # Nombres Persona Natural
    con_pat = fields.Char(string="Apellido Paterno")
    con_mat = fields.Char(string="Apellido Materno")
    con_nom1 = fields.Char(string="Primer Nombre")
    con_nom2 = fields.Char(string="Segundo Nombre")
    con_cas = fields.Char(string="Apellido de Casada")
    
    # Nombres Empresa
    con_raz = fields.Char(string="Razón Social")
    
    # Domicilio
    dom_dpto = fields.Many2one('res.country.state', string="Departamento")
    dom_ciu = fields.Char(string="Ciudad")
    dom_bar = fields.Char(string="Barrio/Zona")
    dom_tipo = fields.Selection([
        ('AV', 'Avenida'),
        ('CA', 'Calle'),
        ('PJ', 'Pasaje'),
        ('PL', 'Plaza')
    ], string="Tipo de Vía")
    dom_nom = fields.Char(string="Nombre de Vía")
    dom_num = fields.Char(string="Número")
    dom_edif = fields.Char(string="Edificio")
    dom_bloq = fields.Char(string="Bloque")
    dom_piso = fields.Char(string="Piso")
    dom_apto = fields.Char(string="Depto/Apto")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('is_contribuyente', False):
                vals['con_pmc'] = self.env['ir.sequence'].next_by_code('catastro.contribuyente.pmc') or 0
        return super(ResPartner, self).create(vals_list)

    @api.onchange('con_tipo', 'con_pat', 'con_mat', 'con_nom1', 'con_nom2', 'con_cas', 'con_raz')
    def _onchange_compute_name(self):
        for rec in self:
            if rec.con_tipo == 'PER':
                names = [rec.con_pat, rec.con_mat, rec.con_cas, rec.con_nom1, rec.con_nom2]
                names = [n for n in names if n]
                rec.name = " ".join(names)
            elif rec.con_tipo == 'EMP':
                rec.name = rec.con_raz

    @api.constrains('con_tipo', 'con_pat', 'con_mat', 'con_nom1', 'con_nom2', 'con_raz', 'con_nit')
    def _check_contribuyente_rules(self):
        for rec in self:
            if rec.is_contribuyente:
                if rec.con_tipo == 'PER':
                    if not rec.con_pat:
                        raise ValidationError("El Apellido Paterno es obligatorio para personas naturales.")
                    if rec.con_mat and not rec.con_pat:
                        raise ValidationError("Si tiene Apellido Materno, debe tener Apellido Paterno.")
                    if rec.con_nom2 and not rec.con_nom1:
                        raise ValidationError("Si tiene Segundo Nombre, debe tener Primer Nombre.")
                elif rec.con_tipo == 'EMP':
                    if not rec.con_raz and not rec.name:
                        raise ValidationError("La Razón Social no puede estar en blanco.")
                    if not rec.con_pat:
                        raise ValidationError("Debe registrar el apellido del representante legal (Apellido Paterno).")
                    if rec.con_nit and not rec.con_nit.isdigit():
                        raise ValidationError("El NIT debe contener sólo números.")

    @api.constrains('dom_bar', 'dom_nom', 'dom_ciu', 'dom_num', 'dom_apto', 'dom_piso')
    def _check_domicilio_rules(self):
        for rec in self:
            if rec.is_contribuyente:
                if (rec.dom_bar or rec.dom_nom) and not rec.dom_ciu:
                    raise ValidationError("Si se llena el Barrio o la Vía, la Ciudad no puede estar en blanco.")
                if rec.dom_num and not rec.dom_nom:
                    raise ValidationError("Si se llena el Número de domicilio, el Nombre de la Vía no puede estar en blanco.")
                if rec.dom_apto and not rec.dom_piso:
                    raise ValidationError("Si se especifica el Apartamento/Depto, se debe indicar el Piso.")

    @api.constrains('doc_num', 'is_contribuyente')
    def _check_unique_doc_num(self):
        for rec in self:
            if rec.is_contribuyente and rec.doc_num:
                domain = [
                    ('doc_num', '=', rec.doc_num),
                    ('is_contribuyente', '=', True),
                    ('id', '!=', rec.id)
                ]
                if self.search_count(domain) > 0:
                    raise ValidationError(f"Ya existe un contribuyente registrado con el documento: {rec.doc_num}")
