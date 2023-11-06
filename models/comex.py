from odoo import models, fields, api, _

class ImportTemplate(models.Model):
    _name = 'comex'
    _description = 'valorizaciones comex'
    
    name = fields.Char(string="Nro Doc",readonly=True,default='New',copy=False)    
    dolar = fields.Float(string="Valor Dolar", required=True, digits=(5,0))
    cif = fields.Float(string="% extra(CIF)", required=True)
    f_import = fields.Date(string="Fecha Importacion", required=True, states={'sent': [('readonly',True)], 'arrived': [('readonly',True)]})
    f_llegada = fields.Datetime("Fecha Llegada")
    proveedor = fields.Many2one('res.partner', string="Proveedor",required=True, readonly=False, states={'sent': [('readonly',True)], 'arrived': [('readonly',True)]})
    producto_line = fields.One2many('comex.line','producto_id', string='linea producto', copy=True, auto_join=True)
    producto2_line = fields.One2many('comex.line','producto_id', string='linea totales producto',help="Valores se actualizan al grabar la orden")
    total35 = fields.Float(string='Total % extra')
    totalm = fields.Float(string='Total Margen')
    company_id = fields.Many2one('res.company','company', default=lambda self: self.env['res.company']._company_default_get('comex'),index=True)
    state = fields.Selection([
        ('draft','Borrador'),
        ('sent','Embarcado'),
        ('arrived','Arrivado')],string='Status',default='draft')
    
    @api.onchange('producto_line')
    def _compute_dolar(self):
        """calcula cfu al cambiar linea"""
        t35 = 0
        tom = 0
        for line in self.producto_line:    
            line.porx = self.cif        
            line.xcfu = self.dolar * line.valor
            line.mxcu = line.xcfu * line.porx / 100
            line.costounidad = line.xcfu + line.mxcu
            line.ganancia = line.valorventa - line.costounidad
            line.total = line.cantidad * line.xcfu
            line.totalx = line.cantidad * line.mxcu
            line.totalimport = line.total + line.totalx
            line.totalventa = line.valorventa * line.cantidad
            line.totalwin = line.totalventa - line.totalimport
            t35 = t35 + line.totalx
            tom = tom + line.totalwin
        self.total35 = t35
        self.totalm = tom
        

    @api.onchange('dolar')
    def _compute_dolar2(self):
        """calcula cfu al cambiar dolar"""
        t35 = 0
        tom = 0
        for line in self.producto_line:
            line.porx = self.cif
            line.xcfu = self.dolar * line.valor
            line.mxcu = line.xcfu * line.porx / 100 
            line.costounidad = line.xcfu + line.mxcu
            line.ganancia = line.valorventa - line.costounidad   
            line.total = line.cantidad * line.xcfu
            line.totalx = line.cantidad * line.mxcu
            line.totalimport = line.total + line.totalx
            line.totalventa = line.valorventa * line.cantidad
            line.totalwin = line.totalventa - line.totalimport
            t35 = t35 + line.totalx
            tom = tom + line.totalwin
        self.total35 = t35
        self.totalm = tom

    @api.onchange('cif')
    def _compute_cif(self):
        """calcula cfu al cambiar cif"""
        t35 = 0
        tom = 0
        for line in self.producto_line:    
            line.porx = self.cif        
            line.xcfu = self.dolar * line.valor
            line.mxcu = line.xcfu * line.porx / 100
            line.costounidad = line.xcfu + line.mxcu
            line.ganancia = line.valorventa - line.costounidad
            line.total = line.cantidad * line.xcfu
            line.totalx = line.cantidad * line.mxcu
            line.totalimport = line.total + line.totalx
            line.totalventa = line.valorventa * line.cantidad
            line.totalwin = line.totalventa - line.totalimport
            t35 = t35 + line.totalx
            tom = tom + line.totalwin
        self.total35 = t35
        self.totalm = tom


    @api.model
    def create(self,vals):
        if vals.get('name','New')=='New':
            vals['name']=self.env['ir.sequence'].next_by_code('abr.comex') or 'New'
        result = super(ImportTemplate,self).create(vals)
        return result

    @api.multi
    def env_inventario(self):
        if self.proveedor:
            for order in self:
                vals = {
                    'move_type': 'direct',
                    'state': 'confirmed',
                    'scheduled_date': self.f_llegada,               
                    'location_id': '17',
                    'location_dest_id': '12',
                    'picking_type_id': 1,
                    'partner_id': self.proveedor.id,
                    'company_id': 1,
                    'origin': self.name
                }
                self.env['stock.picking'].create(vals)   
                alpha_ot= self.env['stock.picking'].search([('origin','=',self.name)])
                for line in order.producto_line:
                    vals = {
                    'name': line.nombre.name,
                    'sequence': '10',
                    'company_id': 1,
                    'date_expected': alpha_ot.scheduled_date,
                    'product_id': line.nombre.id,                
                    'product_uom_qty': line.cantidad,
                    'product_uom': '1',
                    'location_id': '17',
                    'location_dest_id': '12',
                    'picking_id': alpha_ot.id,
                    'state': 'confirmed',
                    'procure_method': 'make_to_stock',
                    'picking_type_id': 1,
                    'reference': alpha_ot.name
                    }
                    self.env['stock.move'].create(vals)
                self.write({
                    'state':'sent'
                    })
                beta_ot= self.env['stock.move'].search([('reference','=',alpha_ot.name)])
                for line in order.producto_line:
                    temp_ot = beta_ot.search([('product_id','=',line.nombre.id)], order="id desc", limit=1)
                    vals = {
                    'picking_id': alpha_ot.id,
                    'move_id': temp_ot.id,
                    'product_id': line.nombre.id,
                    'product_uom_id': '1',
                    'qty_done': line.cantidad,
                    'location_id': '17',
                    'location_dest_id': '12',
                    'state': 'confirmed',
                    'reference': alpha_ot.name
                    }
                    self.env['stock.move.line'].create(vals)
            self.state = 'sent'        
        return

    @api.multi
    def cierre(self):
        self.state = 'arrived'
        for order in self:
            for line in order.producto_line:
                line.write({
                    'state':'arrived'
                    })


    @api.multi
    def valores(self):
        for order in self:
            for line in order.producto_line:
                alpha_ot = self.env['product.template'].search([('id','=',line.nombre.id)])
                alpha_ot.write({
                    'standard_price': line.costounidad,
                    'list_price': line.valorventa,
                    })
        return
    
    
class ImportTemplate_line(models.Model):
    _name = 'comex.line'
    _description = 'linea ingreso de producto'
    
    producto_id = fields.Many2one('comex',string ='id producto',required=True, ondelete='cascade', index=True, copy=False)
    nombre = fields.Many2one('product.template',string="Descripcion",required=True)
    dolar = fields.Float(default='1')
    valor = fields.Float(string="Valor (U$)",required=True, default='1')
    cantidad = fields.Float(string='Cantidad',required=True, default='1')
    porx = fields.Integer(string="Porcentaje Extra", default='1')
    xcfu = fields.Float(string="Costo (FOB) pesos" )
    mxcu = fields.Float(string ="Valor extra")
    total = fields.Float(string = "Total FOB")
    totalx = fields.Float(string = "Total % extra")
    costounidad = fields.Float(string ="Costo Final")
    valorventa = fields.Float(string = "Valor de Venta", default='1')
    ganancia = fields.Float(string = "Margen de Utilidad")
    totalimport = fields.Float(string = "Total Costos")
    totalventa = fields.Float(string = "Total Venta")
    totalwin = fields.Float(string = "Total Margen")
    state = fields.Selection([('draft','Borrador'),('sent','Embarcado'),('arrived','Arrivado')],string='Status',default='draft')


    @api.onchange('valorventa')
    def _compute_venta(self):
        """calcula cfu al cambiar dolar"""
        t35 = 0
        tom = 0
        for line in self:
            line.ganancia = line.valorventa - line.costounidad 
            line.totalventa = line.valorventa * line.cantidad
            line.totalwin = line.totalventa - line.totalimport
            
                
            
    


    

