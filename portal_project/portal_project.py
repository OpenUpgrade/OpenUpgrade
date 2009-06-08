# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields, osv
import pooler
import tools
from tools.config import config
from tools.translate import _
import netsvc
import time

AVAILABLE_STATES = [
    ('draft','Draft'),
    ('open','Open'),
    ('cancel', 'Cancelled'),
    ('done', 'Closed'),
    ('pending','Pending')
]

def _project_get(self, cr, uid, context={}):
    obj = self.pool.get('project.project')
    ids = obj.search(cr, uid, [])
    res = obj.read(cr, uid, ids, ['id','name'], context)
    res = [(str(r['id']),r['name']) for r in res]
    return res
    
class users(osv.osv):
    _inherit = 'res.users'

    _columns = {
          'user_id' : fields.many2one('project.project', 'portal', ondelete='cascade'),
          'context_project_id': fields.selection(_project_get, 'Project',size=128),
        }
    
    _defaults = {
          'context_project_id' : lambda *args: '2',
            }
    
    def context_get(self, cr, uid, context=None):
        res = super(users, self).context_get(cr, uid, context)
        return res
users()

class project_project(osv.osv):
    _inherit = "project.project"
    
    def _get_details(self, cr, uid, ids, context={}, *arg):
        return {}
    
    _columns = {
                'section_bug_id': fields.many2one('crm.case.section','Bug Section'),
                'section_feature_id': fields.many2one('crm.case.section','Feature Section'),
                'section_support_id': fields.many2one('crm.case.section','Support Section'),
                'section_annouce_id': fields.many2one('crm.case.section','Announce Section'),
                'tasks': fields.function(_get_details , type='float', method=True, store=True, string='Tasks', multi='tasks'),
                'bugs' : fields.function(_get_details, type='float', method=True, store=True, string='Bugs', multi='tasks'), 
                'features' : fields.function(_get_details, type='float', method=True, store=True, string='Features',multi='tasks'),
                'support_req' : fields.function(_get_details, type='float', method=True,multi='tasks', store=True, string='Support Requests'),
                'doc' : fields.function(_get_details, type='float', method=True, store=True,multi='tasks', string='Documents'),
                'announce_ids' : fields.one2many('crm.case', 'case_id', 'Announces'),
                'member_ids': fields.one2many('res.users', 'user_id', 'Project Members', help="Project's member. Not used in any computation, just for information purpose."),                
    }
project_project()

class Wiki(osv.osv):
    _inherit="wiki.wiki"
    _columns={
        'project_id' : fields.many2one('project.project', 'Project')      
        }
Wiki()

class crm_case(osv.osv):
    _inherit = 'crm.case'
    _columns = {
                'project_id' : fields.many2one('project.project', 'Project', size=64),
                'bug_ids' : fields.one2many('crm.case', 'case_id', 'Latest Bugs'),
                'section_id' : fields.many2one('crm.case.section', 'Section', required=False)
                }
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None,
            context=None, count=False):
        if context is None:
            context = {}
        if 'section' in context and context['section']=='Bug Tracking':
            cr.execute('select c.id from crm_case c left join project_project p on p.id=c.project_id where c.section_id=p.section_bug_id')
            return map(lambda x: x[0], cr.fetchall())
        elif 'section' in context and context['section']=='Feature':
            cr.execute('select c.id from crm_case c left join project_project p on p.id=c.project_id where c.section_id=p.section_feature_id')
            return map(lambda x: x[0], cr.fetchall())
        elif 'section' in context and context['section']=='Support':
            cr.execute('select c.id from crm_case c left join project_project p on p.id=c.project_id where c.section_id=p.section_support_id')
            return map(lambda x: x[0], cr.fetchall())
        elif 'section' in context and context['section']=='Announce':
            cr.execute('select c.id from crm_case c left join project_project p on p.id=c.project_id where c.section_id=p.section_annouce_id')
            return map(lambda x: x[0], cr.fetchall())
        return super(crm_case, self).search(cr, uid, args, offset, limit,
                order, context=context, count=count) 
    
    def create(self, cr, uid, values, *args, **kwargs):
        case_id = super(crm_case, self).create(cr, uid, values, *args, **kwargs)
        cr.commit()
        case = self.browse(cr, uid, case_id)
        if case.project_id:         
            self.pool.get('project.project')._log_event(cr, uid, case.project_id.id, {
                                'res_id' : case.id,
                                'name' : case.name, 
                                'description' : case.description, 
                                'user_id': uid, 
                                'action' : 'create',
                                'type'   : 'case'})
        return case_id
    
    def write(self, cr, uid, ids, vals, context={}):
        res = super(crm_case, self).write(cr, uid, ids, vals, context={})
        cr.commit()
        cases = self.browse(cr, uid, ids)
        for case in cases:
            if case.project_id:         
                self.pool.get('project.project')._log_event(cr, uid, case.project_id.id, {
                                    'res_id' : case.id,
                                    'name' : case.name, 
                                    'description' : case.description, 
                                    'user_id': uid, 
                                    'action' : 'write',
                                    'type' : 'case'})
        return res
crm_case()

class report_crm_case_bugs(osv.osv):
    _name = "report.crm.case.bugs"
    _description = "Bugs by State"
    _auto = False
    _rec_name = 'user_id'
    _columns = {
        'nbr': fields.integer('# of Cases', readonly=True),
        'state': fields.selection(AVAILABLE_STATES, 'Status', size=16, readonly=True),
        'user_id': fields.many2one('res.users', 'User', size=16, readonly=True),
        'project_id' : fields.many2one('project.project', 'Project', size=64),
        'section_id' : fields.many2one('crm.case.section', 'Section', required=False)
    }
    
    def init(self, cr):
        cr.execute("""
            create or replace view report_crm_case_bugs as (
                select
                    min(c.id) as id,
                    c.user_id,
                    c.project_id as project_id,
                    c.section_id as section_id,
                    count(*) as nbr,
                    c.state
                from
                    crm_case c left join project_project p on p.id = c.project_id
                where c.section_id = p.section_bug_id
                group by c.user_id, c.project_id, c.section_id, c.state
            )""")
report_crm_case_bugs()

class report_project_working_hours(osv.osv):
    _name = "report.project.working.hours"
    _description = "Working hours of the day"
    _auto = False
    _columns = {
        'name': fields.date('Day', readonly=True),
        'user_id':fields.many2one('res.users', 'User', readonly=True),
        'hours': fields.float('Timesheet Hours'),
        'analytic_id' : fields.many2one('account.analytic.account', 'Analytic Account'),
        'description' : fields.text('Description'),
        'amount' : fields.float('Amount', required=True),
    }
    
    def init(self, cr):
        cr.execute("""
            create or replace view report_project_working_hours as (
                select
                    min(c.id) as id,
                    to_char(c.date, 'YYYY-MM-01') as name,
                    c.user_id as user_id,
                    c.unit_amount as hours,
                    c.amount as amount,
                    c.account_id as analytic_id,
                    c.name as description
                from
                    account_analytic_line c
                where 
                    c.account_id in (select category_id from project_project where id = '2')
                group by c.user_id, c.date, c.unit_amount, c.account_id, c.amount, c.name
           )""")
report_project_working_hours()

class report_crm_case_features_user(osv.osv):
    _name = "report.crm.case.features.user"
    _description = "Features by User"
    _auto = False
    _rec_name = 'user_id'
    _columns = {
        'nbr': fields.integer('# of Cases', readonly=True),
        'user_id': fields.many2one('res.users', 'User', size=16, readonly=True),
    }
    def init(self, cr):
        cr.execute("""
            create or replace view report_crm_case_features_user as (
                select
                    min(c.id) as id,
                    c.user_id,
                    count(*) as nbr
                from
                    crm_case c left join project_project p on p.id = c.project_id
                where c.section_id = p.section_feature_id
                group by c.user_id, c.name
            )""")
report_crm_case_features_user()

class report_crm_case_support_user(osv.osv):
    _name = "report.crm.case.support.user"
    _description = "Support by User"
    _auto = False
    _rec_name = 'user_id'
    _columns = {
        'nbr': fields.integer('# of Cases', readonly=True),
        'user_id': fields.many2one('res.users', 'User', size=16, readonly=True),
    }
    def init(self, cr):
        cr.execute("""
            create or replace view report_crm_case_support_user as (
                select
                    min(c.id) as id,
                    c.user_id,
                    count(*) as nbr
                from
                    crm_case c left join project_project p on p.id = c.project_id
                where c.section_id = p.section_support_id
                group by c.user_id, c.name
            )""")
report_crm_case_support_user()

class report_crm_case_announce_user(osv.osv):
    _name = "report.crm.case.announce.user"
    _description = "Announces by User"
    _auto = False
    _rec_name = 'user_id'
    _columns = {
        'nbr': fields.integer('# of Cases', readonly=True),
        'user_id': fields.many2one('res.users', 'User', size=16, readonly=True),
    }
    def init(self, cr):
        cr.execute("""
            create or replace view report_crm_case_announce_user as (
                select
                    min(c.id) as id,
                    c.user_id,
                    count(*) as nbr
                from
                    crm_case c left join project_project p on p.id = c.project_id
                where c.section_id = p.section_annouce_id
                group by c.user_id, c.name
            )""")
report_crm_case_announce_user()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
