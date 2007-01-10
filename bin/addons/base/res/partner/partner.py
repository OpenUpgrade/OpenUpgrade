##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: partner.py 1007 2005-07-25 13:18:09Z kayhman $
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import math

from osv import fields,osv
import tools
import ir
import pooler

class res_partner_function(osv.osv):
	_name = 'res.partner.function'
	_description = 'Function of the contact'
	_columns = {
		'name': fields.char('Name', size=64, required=True),
		'code': fields.char('Code', size=8),
	}
	_order = 'name'
res_partner_function()

class res_country(osv.osv):
	_name = 'res.country'
	_description = 'Country'
	_columns = {
		'name': fields.char('Country Name', size=64, help='The full name of the country.'),
		'code': fields.char('Country Code', size=2, help='The ISO country code in two chars. You can use this field for quick search.'),
	}
	_sql_constraints = [
		('name_uniq', 'unique (name)', 'The name of the country must be unique !'),
		('code_uniq', 'unique (code)', 'The code of the country must be unique !')
	]
	def name_search(self, cr, user, name, args=[], operator='ilike', context={}):
		ids = self.search(cr, user, [('code','=',name)]+ args)
		if not ids:
			ids = self.search(cr, user, [('name',operator,name)]+ args)
		return self.name_get(cr, user, ids)
	_order='code'
res_country()

class res_country_state(osv.osv):
	_description="Country state"
	_name = 'res.country.state'
	_columns = {
		'country_id': fields.many2one('res.country', 'Country'),
		'name': fields.char('State Name', size=64),
		'code': fields.char('State Code', size=2),
	}
	_order = 'code'
res_country_state()

class res_payterm(osv.osv):
	_description = 'Payment term'
	_name = 'res.payterm'
	_columns = {
		'name': fields.char('Payment term (short name)', size=64),
	}
res_payterm()

class res_partner_category_type(osv.osv):
	_description='Partner category types'
	_name = 'res.partner.category.type'
	_columns = {
		'name': fields.char('Category Name', required=True, size=64),
	}
	_order = 'name'
res_partner_category_type()

def _cat_type_get(self, cr, uid, context={}):
	obj = self.pool.get('res.partner.category.type')
	ids = obj.search(cr, uid, [])
	res = obj.read(cr, uid, ids, ['name'], context)
	return [(r['name'], r['name']) for r in res]

class res_partner_category(osv.osv):
	def name_get(self, cr, uid, ids, context={}):
		if not len(ids):
			return []
		reads = self.read(cr, uid, ids, ['name','parent_id'], context)
		res = []
		for record in reads:
			name = record['name']
			if record['parent_id']:
				name = record['parent_id'][1]+' / '+name
			res.append((record['id'], name))
		return res

	def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, unknow_dict):
		res = self.name_get(cr, uid, ids)
		return dict(res)
	def _check_recursion(self, cr, uid, ids):
		level = 100
		while len(ids):
			cr.execute('select distinct parent_id from res_partner_category where id in ('+','.join(map(str,ids))+')')
			ids = filter(None, map(lambda x:x[0], cr.fetchall()))
			if not level:
				return False
			level -= 1
		return True

	_description='Partner Categories'
	_name = 'res.partner.category'
	_columns = {
		'name': fields.char('Category Name', required=True, size=64),
		'type_id': fields.many2one('res.partner.category.type', 'Category Type'),
		'parent_id': fields.many2one('res.partner.category', 'Parent Category', select=True),
		'complete_name': fields.function(_name_get_fnc, method=True, type="char", string='Name'),
		'child_ids': fields.one2many('res.partner.category', 'parent_id', 'Childs Category'),
		'active' : fields.boolean('Active'),
	}
	_constraints = [
		(_check_recursion, 'Error ! You can not create recursive categories.', ['parent_id'])
	]
	_defaults = {
		'active' : lambda *a: 1,
	}
	_order = 'parent_id,name'
res_partner_category()

class res_partner_title(osv.osv):
	_name = 'res.partner.title'
	_columns = {
		'name': fields.char('Title', required=True, size=46, translate=True),
		'shortcut': fields.char('Shortcut', required=True, size=16),
		'domain': fields.selection([('partner','Partner'),('contact','Contact')], 'Domain', required=True, size=24)
	}
	_order = 'name'
res_partner_title()

def _contact_title_get(self, cr, uid, context={}):
	obj = self.pool.get('res.partner.title')
	ids = obj.search(cr, uid, [('domain', '=', 'contact')])
	res = obj.read(cr, uid, ids, ['shortcut','name'], context)
	return [(r['shortcut'], r['name']) for r in res]

def _partner_title_get(self, cr, uid, context={}):
	obj = self.pool.get('res.partner.title')
	ids = obj.search(cr, uid, [('domain', '=', 'partner')])
	res = obj.read(cr, uid, ids, ['shortcut','name'], context)
	return [(r['shortcut'], r['name']) for r in res]

def _lang_get(self, cr, uid, context={}):
	obj = self.pool.get('res.lang')
	ids = obj.search(cr, uid, [])
	res = obj.read(cr, uid, ids, ['code', 'name'], context)
	res = [(r['code'], r['name']) for r in res]
	return res + [(False, '')]

class res_partner(osv.osv):
	_description='Partner'
	_name = "res.partner"
	_order = "name"
	_columns = {
		'name': fields.char('Name', size=128, required=True, select=True),
		'date': fields.date('Date'),
		'title': fields.selection(_partner_title_get, 'Title', size=32),
		'parent_id': fields.many2one('res.partner','Main Company', select=True),
		'child_ids': fields.one2many('res.partner', 'parent_id', 'Partner Ref.'),
		'ref': fields.char('Code', size=64),
		'lang': fields.selection(_lang_get, 'Language', size=5),
		'user_id': fields.many2one('res.users', 'Salesman'),
		'responsible': fields.many2one('res.users', 'Users'),
		'vat': fields.char('VAT',size=32),
		'bank_ids': fields.one2many('res.partner.bank', 'partner_id', 'Banks'),
		'website': fields.char('Website',size=64),
		'comment': fields.text('Notes'),
		'address': fields.one2many('res.partner.address', 'partner_id', 'Contacts'),
		'category_id': fields.many2many('res.partner.category', 'res_partner_category_rel', 'partner_id', 'category_id', 'Categories'),
		'events': fields.one2many('res.partner.event', 'partner_id', 'events'),
		'credit_limit': fields.float(string='Credit Limit'),
		'ean13': fields.char('EAN13', size=13),
		'active': fields.boolean('Active'),
	}
	_defaults = {
		'active': lambda *a: 1,
	}
	_sql_constraints = [
		('name_uniq', 'unique (name)', 'The name of the partner must be unique !')
	]
	
	def _check_ean_key(self, cr, uid, ids):
		for partner_o in pooler.get_pool(cr.dbname).get('res.partner').read(cr, uid, ids, ['ean13',]):
			thisean=partner_o['ean13']
			if thisean and thisean!='':
				if len(thisean)!=13:
					return False
				sum=0
				for i in range(12):
					if not (i % 2):
						sum+=int(thisean[i])
					else:
						sum+=3*int(thisean[i])
				if math.ceil(sum/10.0)*10-sum!=int(thisean[12]):
					return False
		return True

#	_constraints = [(_check_ean_key, 'Error: Invalid ean code', ['ean13'])]

	def name_get(self, cr, uid, ids, context={}):
		if not len(ids):
			return []
		if context.get('show_ref', False):
			rec_name = 'ref'
		else:
			rec_name = 'name'
			
		res = [(r['id'], r[rec_name]) for r in self.read(cr, uid, ids, [rec_name], context)]
		return res
		
	def name_search(self, cr, uid, name, args=[], operator='ilike', context={}, limit=80):
		if name:
			ids = self.search(cr, uid, [('ref', '=', name)] + args, limit=limit)
			if not ids:
				ids = self.search(cr, uid, [('name', operator, name)] + args, limit=limit)
		else:
			ids = self.search(cr, uid, args, limit=limit)
		return self.name_get(cr, uid, ids, context)

	def _email_send(self, cr, uid, ids, email_from, subject, body, on_error=None):
		partners = self.browse(cr, uid, ids)
		for partner in partners:
			if len(partner.address):
				if partner.address[0].email:
					tools.email_send(email_from, [partner.address[0].email], subject, body, on_error)
		return True

	def email_send(self, cr, uid, ids, email_from, subject, body, on_error=''):
		while len(ids):
			self.pool.get('ir.cron').create(cr, uid, {
				'name': 'Send Partner Emails',
				'user_id': uid,
#				'nextcall': False,
				'model': 'res.partner',
				'function': '_email_send',
				'args': repr([ids[:16], email_from, subject, body, on_error])
			})
			ids = ids[16:]
		return True
		
	def address_get(self, cr, uid, ids, adr_pref=['default']):
		cr.execute('select type,id from res_partner_address where partner_id in ('+','.join(map(str,ids))+')')
		res = cr.fetchall()
		adr = dict(res)
		# get the id of the (first) default address if there is one, 
		# otherwise get the id of the first address in the list
		if res:
			default_address = adr.get('default', res[0][1])
		else:
			default_address = False
		result = {}
		for a in adr_pref:
			result[a] = adr.get(a, default_address)
		return result
	
	def gen_next_ref(self, cr, uid, ids):
		if len(ids) != 1:
			return True
			
		# compute the next number ref
		cr.execute("select ref from res_partner where ref is not null order by char_length(ref) desc, ref desc limit 1")
		res = cr.dictfetchall()
		ref = res and res[0]['ref'] or '0'
		try:
			nextref = int(ref)+1
		except e:
			raise osv.except_osv('Warning', "Couldn't generate the next id because some partners have an alphabetic id !")

		# update the current partner
		cr.execute("update res_partner set ref=%d where id=%d", (nextref, ids[0]))
		return True
res_partner()


class res_partner_bank_type(osv.osv):
	_description='Bank Account Type'
	_name = 'res.partner.bank.type'
	_columns = {
		'name': fields.char('Name', size=64, required=True),
		'code': fields.char('Code', size=64),
		'elec_pay': fields.char('Electronic Payment', size=64),
	}
res_partner_bank_type()

class res_partner_bank(osv.osv):
	_description='Bank Details'
	_name = "res.partner.bank"
	_order = "sequence"
	_columns = {
		'name': fields.char('Account Name', size=64, required=True),
		'sequence': fields.integer('Sequence'),
		'number': fields.char('Account Number', size=64), #TODO : plan migration because of fields modifications
		'type_id' : fields.many2one('res.partner.bank.type', 'Account Type', required=True),
		'bank_name': fields.char('Bank Name', size=64),
		'bank_code': fields.char('Bank Code', size=64, help="For example : Swift number or Clearing number."),
		'bank_guichet': fields.char('Branch', size=64),
		'partner_id': fields.many2one('res.partner', 'Partner', required=True, ondelete='cascade', select=True),
		'active': fields.boolean('Active'),
	}
	_defaults = {
		'active': lambda *a: 1,
	}
res_partner_bank()


class res_partner_address(osv.osv):
	_description ='Partner Contact'
	_name = 'res.partner.address'
	_order = 'id'
	_columns = {
		'partner_id': fields.many2one('res.partner', 'Partner', required=True, ondelete='cascade', select=True),
		'type': fields.selection( [ ('default','Default'),('invoice','Invoice'), ('delivery','Delivery'), ('contact','Contact'), ('other','Other') ],'Address Type'),
		'function': fields.many2one('res.partner.function', 'Function', relate=True),
		'title': fields.selection(_contact_title_get, 'Title', size=32),
		'name': fields.char('Contact Name', size=64),
		'street': fields.char('Street', size=128),
		'street2': fields.char('Street2', size=128),
		'zip': fields.char('Zip', change_default=True, size=24),
		'city': fields.char('City', size=128),
		'state_id': fields.many2one("res.country.state", 'State', domain="[('country_id','=',country_id)]"),
		'country_id': fields.many2one('res.country', 'Country'),
		'email': fields.char('E-Mail', size=64),
		'phone': fields.char('Phone', size=64),
		'fax': fields.char('Fax', size=64),
		'mobile': fields.char('Mobile', size=64),
		'birthdate': fields.char('Birthdate', size=64),
		'active': fields.boolean('Active'),
	}
	_defaults = {
		'active': lambda *a: 1,
	}

	def name_get(self, cr, user, ids, context={}):
		if not len(ids):
			return []
		res = []
		for r in self.read(cr, user, ids, ['name','zip','city','partner_id']):
			if context.get('contact_display', 'contact')=='partner':
				res.append((r['id'], r['partner_id'][1]))
			else:
				addr = str(r['name'] or '')
				if r['name'] and (r['zip'] or r['city']):
					addr += ', '
				addr += str(r['zip'] or '') + ' ' + str(r['city'] or '')
				res.append((r['id'], addr))
		return res

	def name_search(self, cr, user, name, args=[], operator='ilike', context={}, limit=80):
		if context.get('contact_display', 'contact')=='partner':
			ids = self.search(cr, user, [('partner_id',operator,name)], limit=limit)
		else:
			ids = self.search(cr, user, [('zip','=',name)] + args, limit=limit)
			if not ids: 
				ids = self.search(cr, user, [('city',operator,name)] + args, limit=limit)
			if not ids:
				ids = self.search(cr, user, [('name',operator,name)] + args, limit=limit)
		return self.name_get(cr, user, ids)
res_partner_address()

# vim:noexpandtab:
