##############################################################################
#
# Copyright (c) 2004 TINY SPRL. (http://tiny.be) All Rights Reserved.
#                    Fabien Pinckaers <fp@tiny.Be>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting FROM its eventual inadequacies AND bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees AND support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it AND/or
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

import pooler
import time
from report import report_sxw

class crossovered_analytic(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(crossovered_analytic, self).__init__(cr, uid, name, context)
        self.localcontext.update( {
            'time': time,
            'lines': self._lines,
            'ref_lines' : self._ref_lines,
            'find_children':self.find_children,
        })
        self.base_amount=0.00

    def find_children(self,ref_ids):
        to_return_ids = []
        for id in ref_ids:
            # to avoid duplicate entries
            if id not in to_return_ids:
                to_return_ids.append(self.pool.get('account.analytic.account').search(self.cr,self.uid,[('parent_id','child_of',[id])]))
        return to_return_ids[0]


    def _ref_lines(self,form):
        result = []
        res = {}
        acc_id = []
        final = []
        acc_pool = self.pool.get('account.analytic.account')
        line_pool = self.pool.get('account.analytic.line')

        self.dict_acc_ref = {}
        if form['journal_ids'][0][2]:
            journal = " in (" + ','.join(map(lambda x: str(x), form['journal_ids'][0][2])) + ")"
        else:
            journal = 'is not null'

        query_general = "select id from account_analytic_line where (journal_id " + journal +") AND date>='"+ str(form['date1']) +"'"" AND date<='" + str(form['date2']) + "'"

        self.cr.execute(query_general)
        l_ids=self.cr.fetchall()
        line_ids = [x[0] for x in l_ids]

        obj_line = line_pool.browse(self.cr,self.uid,line_ids)

        #this structure will be usefull for easily knowing the account_analytic_line that are related to the reference account. At this purpose, we save the move_id of analytic lines.
        self.dict_acc_ref[form['ref']] = []
        children_list = self.pool.get('account.analytic.account').search(self.cr,self.uid,[('parent_id','child_of',[form['ref']])])
        for obj in obj_line:
            if obj.account_id.id in children_list:
                if obj.move_id and obj.move_id.id not in self.dict_acc_ref[form['ref']]:
                    self.dict_acc_ref[form['ref']].append(obj.move_id.id)

        res['ref_name'] = acc_pool.name_get(self.cr,self.uid,[form['ref']])[0][1]

        self.final_list = children_list
        selected_ids = line_pool.search(self.cr,self.uid,[('account_id','in',self.final_list)])

        query="SELECT sum(aal.amount) AS amt, sum(aal.unit_amount) AS qty FROM account_analytic_line AS aal, account_analytic_account AS aaa \
                WHERE aal.account_id=aaa.id AND aal.id IN ("+','.join(map(str,selected_ids))+") AND (aal.journal_id " + journal +") AND aal.date>='"+ str(form['date1']) +"'"" AND aal.date<='" + str(form['date2']) + "'"

        self.cr.execute(query)
        info=self.cr.dictfetchall()

        res['ref_qty']=info[0]['qty']
        res['ref_amt']=info[0]['amt']
        self.base_amount= info[0]['amt']

        result.append(res)
        return result

    def _lines(self,form,ids={}):
        if not ids:
            ids = self.ids

        if form['journal_ids'][0][2]:
            journal=" in (" + ','.join(map(lambda x: str(x), form['journal_ids'][0][2])) + ")"
        else:
            journal= 'is not null'

        acc_pool = self.pool.get('account.analytic.account')
        line_pool=self.pool.get('account.analytic.line')
        acc_id=[]
        final=[]
        child_ids=[]
        self.list_ids=[]

        self.final_list = self.find_children(ids)

        for acc_id in self.final_list:
            selected_ids = line_pool.search(self.cr,self.uid,[('account_id','=',acc_id),('move_id','in',self.dict_acc_ref[form['ref']])])
            if selected_ids:
                query="SELECT sum(aal.amount) AS amt, sum(aal.unit_amount) AS qty,aaa.name as acc_name,aal.account_id as id  FROM account_analytic_line AS aal, account_analytic_account AS aaa \
                WHERE aal.account_id=aaa.id AND aal.id IN ("+','.join(map(str,selected_ids))+") AND (aal.journal_id " + journal +") AND aal.date>='"+ str(form['date1']) +"'"" AND aal.date<='" + str(form['date2']) + "'"" GROUP BY aal.account_id,aaa.name ORDER BY aal.account_id"

                self.cr.execute(query)
                res = self.cr.dictfetchall()
                if res:
                    for element in res:
                        if self.base_amount<>0.00:
                            element['perc']= (element['amt'] / self.base_amount) * 100.00
                        else:
                            element['perc']=0.00
                else:
                    result={}
                    res=[]
                    result['id']=acc_id
                    result['acc_name']=acc_pool.browse(self.cr,self.uid,acc_id).name
                    result['amt']=result['qty']=result['perc']=0.00
                    if not form['empty_line']:
                        res.append(result)
            else:
                result={}
                res=[]
                result['id']=acc_id
                result['acc_name']=acc_pool.browse(self.cr,self.uid,acc_id).name
                result['amt']=result['qty']=result['perc']=0.00
                if not form['empty_line']:
                    res.append(result)

            for item in res:
                obj_acc=acc_pool.name_get(self.cr,self.uid,[item['id']])
                item['acc_name']=obj_acc[0][1]
                final.append(item)
        return final

report_sxw.report_sxw('report.account.analytic.account.crossovered.analytic', 'account.analytic.account', 'addons/account_analytic_plans/report/crossovered_analytic.rml',parser=crossovered_analytic, header=False)

